"""Google Gemini LLM provider adapter with structured output and token tracking."""

import json
import time
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

from .base import BaseLLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """
    Adapter for Google Gemini models (Gemini 2.5 Flash, Gemini 1.5 Pro).
    Utilizes official REST endpoint with JSON Schema constraints and token extraction.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        super().__init__(api_key=api_key, model_name=model_name or "gemini-2.5-flash")
        # Normalize model identifier
        if not self.model_name.startswith("gemini-"):
            self.model_name = f"gemini-{self.model_name}"

    async def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> LLMResult[T]:
        start_time = time.perf_counter()

        if not self.api_key:
            return LLMResult(
                data=None,
                provider="gemini",
                model=self.model_name,
                error="GEMINI_API_KEY environment variable is not configured.",
                latency_seconds=0.0,
            )

        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
            f"?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\nTask and Input:\n{user_prompt}"}],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.15,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(endpoint, json=payload)
                latency = time.perf_counter() - start_time

                if response.status_code != 200:
                    err_msg = f"Gemini API returned status {response.status_code}: {response.text}"
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error=err_msg,
                    )

                res_json = response.json()

                # Extract token usage
                usage = res_json.get("usageMetadata", {})
                in_tokens = usage.get("promptTokenCount")
                out_tokens = usage.get("candidatesTokenCount")

                # Extract content text
                candidates = res_json.get("candidates", [])
                if not candidates:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error="Gemini returned no candidate outputs.",
                    )

                content_parts = candidates[0].get("content", {}).get("parts", [])
                if not content_parts:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        error="Candidate output contained empty parts.",
                    )

                raw_text = content_parts[0].get("text", "").strip()

                # Parse JSON and validate against Pydantic schema
                try:
                    parsed_dict = json.loads(raw_text)
                except json.JSONDecodeError as e:
                    return LLMResult(
                        data=None,
                        provider="gemini",
                        model=self.model_name,
                        latency_seconds=latency,
                        raw_response=raw_text,
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
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_seconds=latency,
                        raw_response=raw_text,
                        error=f"Model JSON failed schema validation: {e}",
                    )

        except Exception as e:
            latency = time.perf_counter() - start_time
            return LLMResult(
                data=None,
                provider="gemini",
                model=self.model_name,
                latency_seconds=latency,
                error=f"Request to Gemini failed: {e}",
            )
