"""Anthropic Claude LLM provider adapter with structured output and token tracking."""

import json
import time
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

from .base import BaseLLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


class AnthropicProvider(BaseLLMProvider):
    """
    Adapter for Anthropic Claude models (Claude 3.5 Haiku, Claude 3.5 Sonnet).
    Utilizes Messages API with structured JSON output instructions.
    """

    def __init__(self, api_key: str, model_name: str = "claude-3-5-haiku-20241022"):
        super().__init__(api_key=api_key, model_name=model_name or "claude-3-5-haiku-20241022")

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
                provider="anthropic",
                model=self.model_name,
                error="ANTHROPIC_API_KEY environment variable is not configured.",
                latency_seconds=0.0,
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        full_system = f"{system_prompt}\n\nIMPORTANT: Respond with pure JSON only matching the required schema. Do not enclose in markdown code fences."

        payload = {
            "model": self.model_name,
            "max_tokens": 4096,
            "system": full_system,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.15,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
                latency = time.perf_counter() - start_time

                if response.status_code != 200:
                    return LLMResult(
                        data=None,
                        provider="anthropic",
                        model=self.model_name,
                        latency_seconds=latency,
                        error=f"Anthropic returned status {response.status_code}: {response.text}",
                    )

                res_json = response.json()
                usage = res_json.get("usage", {})
                in_tokens = usage.get("input_tokens")
                out_tokens = usage.get("output_tokens")
                req_id = res_json.get("id")

                content_blocks = res_json.get("content", [])
                if not content_blocks:
                    return LLMResult(
                        data=None,
                        provider="anthropic",
                        model=self.model_name,
                        latency_seconds=latency,
                        error="Anthropic returned no content blocks.",
                    )

                raw_text = content_blocks[0].get("text", "").strip()

                # Clean possible markdown fences if returned
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                try:
                    parsed_dict = json.loads(raw_text)
                except json.JSONDecodeError as e:
                    return LLMResult(
                        data=None,
                        provider="anthropic",
                        model=self.model_name,
                        latency_seconds=latency,
                        raw_response=raw_text,
                        error=f"Model response was not valid JSON: {e}",
                    )

                try:
                    validated_obj = response_schema.model_validate(parsed_dict)
                    return LLMResult(
                        data=validated_obj,
                        provider="anthropic",
                        model=self.model_name,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_seconds=latency,
                        request_id=req_id,
                        raw_response=raw_text,
                    )
                except ValidationError as e:
                    return LLMResult(
                        data=None,
                        provider="anthropic",
                        model=self.model_name,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_seconds=latency,
                        request_id=req_id,
                        raw_response=raw_text,
                        error=f"Model JSON failed schema validation: {e}",
                    )

        except Exception as e:
            latency = time.perf_counter() - start_time
            return LLMResult(
                data=None,
                provider="anthropic",
                model=self.model_name,
                latency_seconds=latency,
                error=f"Request to Anthropic failed: {e}",
            )
