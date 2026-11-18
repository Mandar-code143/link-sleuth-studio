"""OpenAI LLM provider adapter with structured output and token tracking."""

import json
import time
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

from .base import BaseLLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    """
    Adapter for OpenAI models (GPT-4o mini, GPT-4o).
    Utilizes Chat Completions JSON mode with token usage logging.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key=api_key, model_name=model_name or "gpt-4o-mini")

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
                provider="openai",
                model=self.model_name,
                error="OPENAI_API_KEY environment variable is not configured.",
                latency_seconds=0.0,
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.15,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                latency = time.perf_counter() - start_time

                if response.status_code != 200:
                    return LLMResult(
                        data=None,
                        provider="openai",
                        model=self.model_name,
                        latency_seconds=latency,
                        error=f"OpenAI returned status {response.status_code}: {response.text}",
                    )

                res_json = response.json()
                usage = res_json.get("usage", {})
                in_tokens = usage.get("prompt_tokens")
                out_tokens = usage.get("completion_tokens")
                req_id = res_json.get("id")

                choices = res_json.get("choices", [])
                if not choices:
                    return LLMResult(
                        data=None,
                        provider="openai",
                        model=self.model_name,
                        latency_seconds=latency,
                        error="OpenAI returned no completion choices.",
                    )

                raw_text = choices[0].get("message", {}).get("content", "").strip()

                try:
                    parsed_dict = json.loads(raw_text)
                except json.JSONDecodeError as e:
                    return LLMResult(
                        data=None,
                        provider="openai",
                        model=self.model_name,
                        latency_seconds=latency,
                        raw_response=raw_text,
                        error=f"Model response was not valid JSON: {e}",
                    )

                try:
                    validated_obj = response_schema.model_validate(parsed_dict)
                    return LLMResult(
                        data=validated_obj,
                        provider="openai",
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
                        provider="openai",
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
                provider="openai",
                model=self.model_name,
                latency_seconds=latency,
                error=f"Request to OpenAI failed: {e}",
            )
