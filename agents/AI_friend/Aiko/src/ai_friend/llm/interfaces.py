from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_friend.llm.models import LLMRequest, LLMResponse


class LLMProvider(ABC):
    """Generates a response from an explicit request and runtime context."""

    @abstractmethod
    def generate(self, request: "LLMRequest") -> "LLMResponse": ...

