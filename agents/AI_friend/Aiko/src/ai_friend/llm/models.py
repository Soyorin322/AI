from dataclasses import dataclass

from ai_friend.runtime.context import RuntimeContext


@dataclass(frozen=True, slots=True)
class LLMRequest:
    input_text: str
    context: RuntimeContext


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: str
    provider: str

