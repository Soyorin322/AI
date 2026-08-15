from ai_friend.llm.interfaces import LLMProvider
from ai_friend.llm.models import LLMRequest, LLMResponse


class MockLLMProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content=f"Mock response to: {request.input_text}", provider="mock")

