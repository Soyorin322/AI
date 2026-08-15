from pathlib import Path

import pytest

from ai_friend.character.mock import MockCharacterProvider
from ai_friend.character.models import CharacterIdentity, CharacterProfile, CharacterState
from ai_friend.knowledge.memory_store import InMemoryKnowledgeStore
from ai_friend.llm.mock import MockLLMProvider
from ai_friend.memory.memory_store import InMemoryMemoryStore
from ai_friend.runtime.orchestrator import RuntimeOrchestrator
from ai_friend.skills.registry import DirectorySkillRegistry


@pytest.fixture
def runtime(tmp_path: Path) -> RuntimeOrchestrator:
    profile = CharacterProfile(CharacterIdentity("test", "Test"), "Test profile", CharacterState())
    return RuntimeOrchestrator(
        MockCharacterProvider(profile),
        InMemoryKnowledgeStore(),
        InMemoryMemoryStore(),
        DirectorySkillRegistry(tmp_path),
        MockLLMProvider(),
    )

