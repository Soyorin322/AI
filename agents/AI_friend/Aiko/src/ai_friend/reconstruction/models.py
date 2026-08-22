from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from ai_friend.core.models import utc_now
from ai_friend.reconstruction.provenance import Lineage


@dataclass(frozen=True, slots=True)
class TemporalScope:
    """Optional, format-neutral point or interval in character/source time."""

    start: str | None = None
    end: str | None = None
    label: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Identity and generic locator for source material."""

    id: str
    title: str
    locator: str
    media_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SourceUnit:
    """Addressable source content; it is not an interpretation."""

    id: str
    source_id: str
    content: str
    locator: str | None = None
    temporal_scope: TemporalScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ObservationRecord:
    """A recorded observation derived from source content."""

    id: str
    content: str
    lineage: Lineage
    temporal_scope: TemporalScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EventRecord:
    """Minimal event boundary without final event-interpretation semantics."""

    id: str
    description: str
    lineage: Lineage
    temporal_scope: TemporalScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceStance(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Traceable evidence; distinct from the claim it may inform."""

    id: str
    content: str
    stance: EvidenceStance
    lineage: Lineage
    temporal_scope: TemporalScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ArtifactStatus(StrEnum):
    CANDIDATE = "candidate"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNRESOLVED = "unresolved"
    CONSOLIDATED = "consolidated"


@dataclass(frozen=True, slots=True)
class StatusTransition:
    """An explicit, auditable maturity change rather than implicit promotion."""

    from_status: ArtifactStatus
    to_status: ArtifactStatus
    reason: str
    timestamp: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class CharacterClaim:
    """A hypothesis about character state, never evidence by itself."""

    id: str
    statement: str
    status: ArtifactStatus
    lineage: Lineage
    transitions: tuple[StatusTransition, ...] = ()
    temporal_scope: TemporalScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CharacterStateSnapshot:
    """Versioned reconstruction result, separate from RuntimeContext."""

    id: str
    version: int
    lineage: Lineage
    temporal_scope: TemporalScope | None = None
    previous_snapshot_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class ReconstructionBundle:
    """One immutable repository revision of reconstruction artifacts."""

    id: str
    version: int
    sources: tuple[SourceReference, ...] = ()
    source_units: tuple[SourceUnit, ...] = ()
    observations: tuple[ObservationRecord, ...] = ()
    events: tuple[EventRecord, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()
    claims: tuple[CharacterClaim, ...] = ()
    snapshots: tuple[CharacterStateSnapshot, ...] = ()
    previous_version: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

