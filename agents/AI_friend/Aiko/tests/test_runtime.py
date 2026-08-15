from pathlib import Path

from ai_friend.bootstrap import build_runtime
from ai_friend.llm.interfaces import LLMProvider
from ai_friend.llm.models import LLMRequest, LLMResponse
from ai_friend.perception.models import PerceptionEvent
from ai_friend.runtime.orchestrator import RuntimeOrchestrator


def test_runtime_processes_text(runtime: RuntimeOrchestrator) -> None:
    assert runtime.process_text("Hello").content == "Mock response to: Hello"
    assert len(runtime.session.messages) == 2


def test_runtime_processes_perception(runtime: RuntimeOrchestrator) -> None:
    event = PerceptionEvent(modality="text", source="test", payload="Observed")
    assert runtime.process_event(event).content == "Mock response to: Observed"


def test_llm_is_replaceable(runtime: RuntimeOrchestrator) -> None:
    class AlternativeFakeLLM(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(f"Alternative: {request.input_text}", "alternative-fake")

    runtime._llm = AlternativeFakeLLM()
    assert runtime.process_text("Hi").provider == "alternative-fake"


def test_composition_root_builds_demo() -> None:
    root = Path(__file__).resolve().parents[1]
    assert build_runtime(root).process_text("Hello").content == "Mock response to: Hello"

