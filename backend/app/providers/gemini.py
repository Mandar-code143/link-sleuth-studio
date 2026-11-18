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
                if not raw_text.strip():
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Gemini returned an empty response.",
                    )

                try:
                    parsed_dict = json.loads(raw_text)
                except json.JSONDecodeError as e:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
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
                err_str = str(e)
                latency = time.perf_counter() - start_time
                error_code, clean_msg = self._classify_error(err_str)
                logger.error(f"Gemini SDK execution failed [{error_code}]: {clean_msg}")
                return LLMResult(
                    data=None,
                    provider="gemini",
                    model=self.model_name,
                    latency_seconds=latency,
                    error_code=error_code,
                    error=clean_msg,
                )

        # 3. Header-authenticated REST Fallback (Never API key in URL!)
        return await self._analyze_via_rest(system_prompt, user_prompt, response_schema, start_time)

    async def _analyze_via_rest(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
        start_time: float,
    ) -> LLMResult[T]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,  # Secure header auth
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System Directive:\n{system_prompt}\n\nTask and Input:\n{user_prompt}"}],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.15,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                latency = time.perf_counter() - start_time

                if response.status_code != 200:
                    error_code, clean_msg = self._classify_http_error(response.status_code, response.text)
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
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
                        model=self.model_name,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Gemini returned no candidate outputs.",
                    )

                content_parts = candidates[0].get("content", {}).get("parts", [])
                if not content_parts:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error_code="AI_INVALID_RESPONSE",
                        error="Candidate output contained empty parts.",
                    )

                raw_text = content_parts[0].get("text", "").strip()
                parsed_dict = json.loads(raw_text)
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

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout):
            latency = time.perf_counter() - start_time
            return LLMResult(
                data=None,
                provider="gemini",
                model=self.model_name,
                latency_seconds=latency,
                error_code="AI_PROVIDER_TIMEOUT",
                error=f"Gemini request timed out while communicating with upstream service.",
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            error_code, clean_msg = self._classify_error(str(e))
            return LLMResult(
                data=None,
                provider="gemini",
                model=self.model_name,
                latency_seconds=latency,
                error_code=error_code,
                error=clean_msg,
            )

    def _classify_error(self, err_msg: str) -> tuple[str, str]:
        """Classifies SDK exception messages into structured error codes without leaking secrets."""
        low = err_msg.lower()
        if "api_key_invalid" in low or "unauthenticated" in low or "invalid api key" in low or "401" in low or "403" in low:
            return "AI_PROVIDER_AUTH_FAILED", "Authentication failed. The configured GEMINI_API_KEY is invalid or unauthorized."
        if "resource_exhausted" in low or "quota" in low:
            return "AI_PROVIDER_QUOTA_EXCEEDED", "Gemini API quota exceeded for the configured project/key."
        if "rate limit" in low or "429" in low:
            return "AI_PROVIDER_RATE_LIMITED", "Gemini API rate limit reached. Please retry after a brief delay."
        if "not_found" in low or "model not found" in low or "404" in low:
            return "AI_MODEL_UNAVAILABLE", f"Model '{self.model_name}' is unavailable or not recognized."
        if "deadline" in low or "timed out" in low or "timeout" in low:
            return "AI_PROVIDER_TIMEOUT", "Upstream Gemini request timed out."
        return "AI_PROVIDER_ERROR", "An upstream error occurred during AI intelligence synthesis."

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
