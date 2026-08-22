from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from ai_friend.core.models import utc_now


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """Minimal Aiko-owned experience record.

    Memory taxonomy is intentionally deferred. Implementations may use metadata
    for provisional classification without making a research candidate part of
    the framework contract.
    """

    id: str
    content: str
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)
    event_ids: tuple[str, ...] = ()
    period_id: str | None = None
    remembered_content: str | None = None
    subjective_meaning: str | None = None
    affective_trace: str | None = None
    uncertainty: str | None = None
    accessible_fact_ids: tuple[str, ...] = ()


class MemoryFormationOutcome(StrEnum):
    PERSIST = "persist"
    DO_NOT_PERSIST = "do_not_persist"


@dataclass(frozen=True, slots=True)
class MemoryFormationDecision:
    event_id: str
    outcome: MemoryFormationOutcome
    reason: str
    memory_id: str | None = None


@dataclass(frozen=True, slots=True)
class MemoryIndexMetadata:
    memory_id: str
    entities: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()
    period_id: str | None = None
    importance: str | None = None
    relationship_relevance: tuple[str, ...] = ()
