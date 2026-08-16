from dataclasses import dataclass

from ai_friend.character.models import CharacterProfile
from ai_friend.knowledge.models import KnowledgeRecord
from ai_friend.memory.models import MemoryRecord
from ai_friend.perception.models import PerceptionEvent
from ai_friend.skills.models import SkillMetadata


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Temporary, per-request view composed for a reasoning provider.

    This is not canonical character storage and must not be persisted as the
    character database. It contains only the data selected for the current turn.
    """

    character: CharacterProfile
    knowledge: tuple[KnowledgeRecord, ...]
    memories: tuple[MemoryRecord, ...]
    skills: tuple[SkillMetadata, ...]
    perception: PerceptionEvent | None = None
