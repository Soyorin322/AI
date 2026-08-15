"""Composition root: concrete adapters are selected only here."""

from pathlib import Path

import yaml

from ai_friend.character.mock import MockCharacterProvider
from ai_friend.character.models import CharacterIdentity, CharacterProfile, CharacterState
from ai_friend.knowledge.memory_store import InMemoryKnowledgeStore
from ai_friend.llm.mock import MockLLMProvider
from ai_friend.memory.memory_store import InMemoryMemoryStore
from ai_friend.runtime.orchestrator import RuntimeOrchestrator
from ai_friend.skills.registry import DirectorySkillRegistry


def build_runtime(project_root: Path) -> RuntimeOrchestrator:
    config_path = project_root / "characters" / "example" / "character.yaml"
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    profile = CharacterProfile(
        identity=CharacterIdentity(id=config["id"], name=config["name"]),
        description=config["description"],
        state=CharacterState(),
    )
    return RuntimeOrchestrator(
        character=MockCharacterProvider(profile),
        knowledge=InMemoryKnowledgeStore(),
        memory=InMemoryMemoryStore(),
        skills=DirectorySkillRegistry(project_root / "skills"),
        llm=MockLLMProvider(),
    )

