from copy import deepcopy
from pathlib import Path

from ai_friend.bootstrap import build_runtime
from ai_friend.character.mock import MockCharacterProvider
from ai_friend.character.models import CharacterIdentity, CharacterProfile, CharacterState
from ai_friend.knowledge.memory_store import InMemoryKnowledgeStore
from ai_friend.llm.interfaces import LLMProvider
from ai_friend.llm.models import LLMRequest, LLMResponse
from ai_friend.memory.memory_store import InMemoryMemoryStore
from ai_friend.perception.models import PerceptionEvent
from ai_friend.runtime.orchestrator import RuntimeOrchestrator
from ai_friend.skills.registry import DirectorySkillRegistry


def test_runtime_processes_text(runtime: RuntimeOrchestrator) -> None:
    assert runtime.process_text("Hello").content == "Mock response to: Hello"
    assert len(runtime.session.messages) == 2


def test_llm_is_replaceable_without_changing_runtime(tmp_path: Path) -> None:
    class AlternativeFakeLLM(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(f"Alternative: {request.input_text}", "alternative-fake")

    profile = CharacterProfile(CharacterIdentity("test", "Test"), "Test profile", CharacterState())
    runtime = RuntimeOrchestrator(
        MockCharacterProvider(profile),
        InMemoryKnowledgeStore(),
        InMemoryMemoryStore(),
        DirectorySkillRegistry(tmp_path),
        AlternativeFakeLLM(),
    )
    assert runtime.process_text("Hi").provider == "alternative-fake"


def test_context_is_composed_for_llm_and_perception_does_not_mutate_character(tmp_path: Path) -> None:
    class CapturingLLM(LLMProvider):
        request: LLMRequest | None = None

        def generate(self, request: LLMRequest) -> LLMResponse:
            self.request = request
            return LLMResponse("captured", "capturing-fake")

    profile = CharacterProfile(
        CharacterIdentity("test", "Test"),
        "Test profile",
        CharacterState({"mood": "neutral"}),
    )
    provider = MockCharacterProvider(profile)
    llm = CapturingLLM()
    runtime = RuntimeOrchestrator(
        provider,
        InMemoryKnowledgeStore(),
        InMemoryMemoryStore(),
        DirectorySkillRegistry(tmp_path),
        llm,
    )
    before = deepcopy(provider.profile())
    event = PerceptionEvent(modality="text", source="test", payload="Observed")

    assert runtime.process_event(event).content == "captured"
    assert llm.request is not None
    assert llm.request.context.perception is event
    assert llm.request.context.character is profile
    assert provider.profile() == before


def test_composition_root_builds_demo() -> None:
    root = Path(__file__).resolve().parents[1]
    assert build_runtime(root).process_text("Hello").content == "Mock response to: Hello"
