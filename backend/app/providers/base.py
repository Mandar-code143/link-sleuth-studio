"""Base abstraction and result container for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMResult(Generic[T]):
    """Structured container for LLM execution outputs, metadata, and token usage."""
    data: Optional[T]
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_seconds: float = 0.0
    request_id: Optional[str] = None
    raw_response: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @property
    def total_tokens(self) -> Optional[int]:
        if self.input_tokens is not None and self.output_tokens is not None:
            return self.input_tokens + self.output_tokens
        return None


class BaseLLMProvider(ABC):
    """Abstract interface all model provider adapters must implement."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
    ) -> LLMResult[T]:
        """
        Executes a prompt against the provider and returns structured validated output.
        """
        pass
