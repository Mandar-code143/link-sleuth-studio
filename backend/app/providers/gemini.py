"""Google Gemini LLM provider adapter using official google-genai SDK and secure REST header auth."""

import json
import logging
import time
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None

from .base import BaseLLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger("linkintel.gemini")


def extract_json_payload(raw_text: str) -> str:
    """Strips markdown code blocks (```json ... ```) or surrounding whitespace to extract raw JSON."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    if text.startswith("```"):
        first_line_end = text.find("\n")
        if first_line_end != -1:
            text = text[first_line_end + 1 :]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


class GeminiProvider(BaseLLMProvider):
    """
    Adapter for Google Gemini models (gemini-2.5-flash, gemini-1.5-flash).
    Supports official google-genai SDK with native Pydantic schema mode and header-authenticated REST.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        clean_model = (model_name or "gemini-2.5-flash").strip().strip("'\"")
        if not clean_model.startswith("gemini-"):
            clean_model = f"gemini-{clean_model}"
        super().__init__(api_key=(api_key or "").strip().strip("'\""), model_name=clean_model)

    async def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> LLMResult[T]:
        start_time = time.perf_counter()

        # 1. Check if API key is configured
        if not self.api_key:
            return LLMResult(
                data=None,
                provider="gemini",
                model=self.model_name,
                latency_seconds=0.0,
                error_code="AI_PROVIDER_NOT_CONFIGURED",
                error="Google Gemini API key is not configured. Set GEMINI_API_KEY in backend/.env.",
            )

        # 2. Prefer official google-genai SDK
        if genai is not None:
            try:
                client = genai.Client(api_key=self.api_key)
                config = genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.15,
                )

                response = await client.aio.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=config,
                )
                latency = time.perf_counter() - start_time

                in_tokens = None
                out_tokens = None
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    in_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
                    out_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

                raw_text = response.text or ""
                clean_json_str = extract_json_payload(raw_text)
                if not clean_json_str:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Gemini returned an empty response.",
                    )

                try:
                    parsed_dict = json.loads(clean_json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"SDK response JSON parse error: {e}. Attempting REST fallback...")
                    # Fall through to REST fallback if JSON decode fails
                    parsed_dict = None

                if parsed_dict is not None:
                    try:
                        validated_obj = response_schema.model_validate(parsed_dict)
                        return LLMResult(
                            data=validated_obj,
                            provider="gemini",
                            model=self.model_name,
                            input_tokens=in_tokens,
                            output_tokens=out_tokens,
                            latency_seconds=latency,
                            raw_response=raw_text,
                        )
                    except ValidationError as e:
                        return LLMResult(
                            data=None,
                            provider="gemini",
                            model=self.model_name,
                            latency_seconds=latency,
                            raw_response=raw_text,
                            error_code="AI_SCHEMA_VALIDATION_FAILED",
                            error=f"Structured schema validation failed: {e}",
                        )

            except Exception as e:
                error_code, clean_msg = self._classify_error(e)
                logger.warning(f"Gemini SDK execution failed [{error_code}]: {clean_msg}. Attempting REST fallback...")
                if error_code == "AI_PROVIDER_AUTH_FAILED":
                    latency = time.perf_counter() - start_time
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error_code=error_code,
                        error=clean_msg,
                    )
                # For non-auth SDK exceptions, proceed to REST fallback

        # 3. Header-authenticated REST Fallback (Never API key in URL!)
        return await self._analyze_via_rest(system_prompt, user_prompt, response_schema, start_time)

    async def _analyze_via_rest(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
        start_time: float,
        model_override: Optional[str] = None,
    ) -> LLMResult[T]:
        active_model = model_override or self.model_name
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,  # Secure header auth
        }

        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.15,
        }

        try:
            # Pass schema to REST generationConfig
            schema_dict = response_schema.model_json_schema()
            generation_config["response_schema"] = schema_dict
        except Exception as e:
            logger.debug(f"Could not convert response_schema to json_schema: {e}")

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": generation_config,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                latency = time.perf_counter() - start_time

                if response.status_code != 200:
                    # If primary model is unavailable (404/503), try fallback to gemini-1.5-flash
                    if response.status_code in (404, 503) and active_model != "gemini-1.5-flash":
                        logger.warning(f"Model {active_model} returned {response.status_code}. Retrying with gemini-1.5-flash fallback...")
                        return await self._analyze_via_rest(
                            system_prompt, user_prompt, response_schema, start_time, model_override="gemini-1.5-flash"
                        )

                    error_code, clean_msg = self._classify_http_error(response.status_code, response.text)
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=active_model,
                        latency_seconds=latency,
                        error_code=error_code,
                        error=clean_msg,
                    )

                res_json = response.json()
                usage = res_json.get("usageMetadata", {})
                in_tokens = usage.get("promptTokenCount")
                out_tokens = usage.get("candidatesTokenCount")

                candidates = res_json.get("candidates", [])
                if not candidates:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=active_model,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Gemini returned no candidate outputs.",
                    )

                content_parts = candidates[0].get("content", {}).get("parts", [])
                if not content_parts:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=active_model,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Candidate output contained empty parts.",
                    )

                raw_text = content_parts[0].get("text", "").strip()
                clean_json_str = extract_json_payload(raw_text)

                try:
                    parsed_dict = json.loads(clean_json_str)
                except json.JSONDecodeError as e:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=active_model,
                        latency_seconds=latency,
                        raw_response=raw_text,
                        error_code="AI_INVALID_RESPONSE",
                        error=f"Model response was not valid JSON: {e}",
                    )

                try:
                    validated_obj = response_schema.model_validate(parsed_dict)
                    return LLMResult(
                        data=validated_obj,
                        provider="gemini",
                        model=active_model,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_seconds=latency,
                        raw_response=raw_text,
                    )
                except ValidationError as e:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=active_model,
                        latency_seconds=latency,
                        raw_response=raw_text,
                        error_code="AI_SCHEMA_VALIDATION_FAILED",
                        error=f"Structured schema validation failed: {e}",
                    )

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout):
            latency = time.perf_counter() - start_time
            return LLMResult(
                data=None,
                provider="gemini",
                model=active_model,
                latency_seconds=latency,
                error_code="AI_PROVIDER_TIMEOUT",
                error="Gemini request timed out while communicating with upstream service.",
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            error_code, clean_msg = self._classify_error(e)
            return LLMResult(
                data=None,
                provider="gemini",
                model=active_model,
                latency_seconds=latency,
                error_code=error_code,
                error=clean_msg,
            )

    def _classify_error(self, exc: Exception | str) -> tuple[str, str]:
        """Classifies SDK exception messages into structured error codes without leaking secrets."""
        err_msg = str(exc)
        code = getattr(exc, "code", None)
        status = getattr(exc, "status", None)
        low = err_msg.lower()

        # Sanitize error message to prevent secret exposure
        clean_diagnostic = err_msg.replace(self.api_key, "[REDACTED]") if self.api_key else err_msg
        clean_diagnostic = clean_diagnostic[:250].strip()

        # Auth failure (401, 403, UNAUTHENTICATED, PERMISSION_DENIED)
        if code in (401, 403) or status in ("UNAUTHENTICATED", "PERMISSION_DENIED") or any(
            x in low for x in ("api_key_invalid", "unauthenticated", "invalid api key", "permission_denied")
        ):
            return "AI_PROVIDER_AUTH_FAILED", "Authentication failed. The configured GEMINI_API_KEY is invalid or unauthorized."

        # Quota / Rate limit (429, RESOURCE_EXHAUSTED)
        if code == 429 or status == "RESOURCE_EXHAUSTED" or "quota" in low or "resource_exhausted" in low or "rate limit" in low:
            if "quota" in low or "exhausted" in low:
                return "AI_PROVIDER_QUOTA_EXCEEDED", "Gemini API quota exceeded for the configured project/key."
            return "AI_PROVIDER_RATE_LIMITED", "Gemini API rate limit reached. Please retry after a brief delay."

        # Model unavailable / Not found (404, 503)
        if code in (404, 503) or status in ("NOT_FOUND", "UNAVAILABLE") or any(
            x in low for x in ("not_found", "model not found", "is not supported for generatecontent", "unavailable", "overloaded")
        ):
            return "AI_MODEL_UNAVAILABLE", f"Model '{self.model_name}' is unavailable or not recognized."

        # Timeout
        if any(x in low for x in ("deadline", "timed out", "timeout")):
            return "AI_PROVIDER_TIMEOUT", "Upstream Gemini request timed out."

        # Schema / Validation error
        if isinstance(exc, ValidationError) or "validationerror" in low or "validation error" in low:
            return "AI_SCHEMA_VALIDATION_FAILED", f"Structured schema validation failed: {clean_diagnostic}"
        if isinstance(exc, json.JSONDecodeError) or "jsondecodeerror" in low:
            return "AI_INVALID_RESPONSE", f"Model response was not valid JSON: {clean_diagnostic}"

        return "AI_PROVIDER_ERROR", f"An upstream error occurred during AI intelligence synthesis: {clean_diagnostic}"

    def _classify_http_error(self, status_code: int, response_text: str) -> tuple[str, str]:
        """Classifies REST HTTP error responses."""
        if status_code in (401, 403):
            return "AI_PROVIDER_AUTH_FAILED", "Authentication failed with Google Gemini. Check GEMINI_API_KEY."
        if status_code == 404:
            return "AI_MODEL_UNAVAILABLE", f"Configured Gemini model '{self.model_name}' was not found."
        if status_code == 429:
            if "quota" in response_text.lower():
                return "AI_PROVIDER_QUOTA_EXCEEDED", "Gemini API quota exceeded."
            return "AI_PROVIDER_RATE_LIMITED", "Gemini rate limit exceeded. Retry later."
        if status_code >= 500:
            return "AI_PROVIDER_ERROR", f"Google Gemini upstream server error (HTTP {status_code})."
        return "AI_PROVIDER_ERROR", f"Gemini API returned HTTP {status_code}."
