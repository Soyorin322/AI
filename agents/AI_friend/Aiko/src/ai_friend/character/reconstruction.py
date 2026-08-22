"""Character-owned historical state contracts produced by reconstruction."""

from dataclasses import dataclass, field
from enum import StrEnum

from ai_friend.reconstruction.models import ArtifactStatus, TemporalScope
from ai_friend.reconstruction.provenance import Lineage


class TraitDomain(StrEnum):
    PERSONALITY = "personality"
    PHYSICAL = "physical"
    MOTIVATION = "motivation"
    BACKSTORY = "backstory"
    EMOTION = "emotion"
    RELATIONSHIPS = "relationships"
    GROWTH = "growth"
    CONFLICT = "conflict"


class DomainEvidenceState(StrEnum):
    OBSERVED = "observed"
    BOUNDED_INFERENCE = "bounded_inference"
    UNKNOWN = "unknown"
    UNCHANGED = "unchanged"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class DomainEntry:
    state: DomainEvidenceState
    statements: tuple[str, ...] = ()
    event_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    uncertainty: str | None = None


def _insufficient() -> DomainEntry:
    return DomainEntry(DomainEvidenceState.INSUFFICIENT_EVIDENCE)


@dataclass(frozen=True, slots=True)
class PeriodDomains:
    personality: DomainEntry = field(default_factory=_insufficient)
    physical: DomainEntry = field(default_factory=_insufficient)
    motivation: DomainEntry = field(default_factory=_insufficient)
    backstory: DomainEntry = field(default_factory=_insufficient)
    emotion: DomainEntry = field(default_factory=_insufficient)
    relationships: DomainEntry = field(default_factory=_insufficient)
    growth: DomainEntry = field(default_factory=_insufficient)
    conflict: DomainEntry = field(default_factory=_insufficient)


@dataclass(frozen=True, slots=True)
class KnowledgeBoundary:
    """Latest period/order and explicitly accessible fact IDs for this state."""

    as_of_period_order: int
    accessible_fact_ids: tuple[str, ...] = ()
    excluded_fact_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PeriodCharacterState:
    id: str
    period_id: str
    temporal_scope: TemporalScope
    knowledge_boundary: KnowledgeBoundary
    domains: PeriodDomains
    supporting_event_ids: tuple[str, ...] = ()
    supporting_evidence_ids: tuple[str, ...] = ()
    status: ArtifactStatus = ArtifactStatus.CANDIDATE
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class ChangeResistance:
    """Evidence-linked qualitative representation, never derived from confidence."""

    value: str
    rationale: str
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class HistoricalAdaptation:
    statement: str
    period_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class CausalHypothesis:
    statement: str
    supporting_evidence_ids: tuple[str, ...]
    counterevidence_ids: tuple[str, ...] = ()
    alternative_hypotheses: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class AccessibilityProfile:
    pattern: str
    period_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class HabitualProcessingPattern:
    pattern: str
    period_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class DevelopmentRecord:
    id: str
    statement: str
    period_state_ids: tuple[str, ...]
    lineage: Lineage
    confidence: str | None = None
    change_resistance: ChangeResistance | None = None
    historical_adaptations: tuple[HistoricalAdaptation, ...] = ()
    causal_hypotheses: tuple[CausalHypothesis, ...] = ()
    accessibility_profiles: tuple[AccessibilityProfile, ...] = ()
    habitual_processing: tuple[HabitualProcessingPattern, ...] = ()
    temporal_scope: TemporalScope | None = None
    status: ArtifactStatus = ArtifactStatus.CANDIDATE


class SkillAcquisitionOrigin(StrEnum):
    CANON_SUPPORTED = "canon_supported"
    POST_CANON_LEARNED = "post_canon_learned"


@dataclass(frozen=True, slots=True)
class SkillEvidence:
    id: str
    event_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    demonstrated_behaviors: tuple[str, ...] = ()
    explicit_training: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CharacterSkillProfile:
    id: str
    skill_id: str
    origin: SkillAcquisitionOrigin
    canonical_proficiency: str
    skill_evidence_ids: tuple[str, ...]
    period_id: str | None = None
    limitations: tuple[str, ...] = ()
    uncertainty: str | None = None


@dataclass(frozen=True, slots=True)
class CompiledStateEntry:
    statement: str
    period_state_ids: tuple[str, ...]
    development_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CompiledCharacterState:
    id: str
    schema_version: str
    character_version: str
    current_period_state_id: str
    historical_period_state_ids: tuple[str, ...]
    entries: tuple[CompiledStateEntry, ...]
    development_ids: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()
