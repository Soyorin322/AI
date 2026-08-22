from dataclasses import replace

from ai_friend.character.reconstruction import (
    CausalHypothesis,
    CharacterSkillProfile,
    ChangeResistance,
    CompiledCharacterState,
    CompiledStateEntry,
    DevelopmentRecord,
    DomainEntry,
    DomainEvidenceState,
    KnowledgeBoundary,
    PeriodCharacterState,
    PeriodDomains,
    SkillAcquisitionOrigin,
    SkillEvidence,
    TraitDomain,
)
from ai_friend.memory.models import MemoryFormationDecision, MemoryFormationOutcome, MemoryRecord
from ai_friend.reconstruction.hardening import ReconstructionGraph, validate_reconstruction_graph
from ai_friend.reconstruction.models import (
    ArtifactStatus,
    BoundaryStatus,
    EventRecord,
    EvidenceRecord,
    EvidenceStance,
    ObservationRecord,
    PeriodAssignment,
    PeriodDefinition,
    ReconstructionBundle,
    SourceReference,
    SourceUnit,
    SourceUnitGrounding,
    TemporalScope,
)
from ai_friend.reconstruction.provenance import Lineage
from ai_friend.reconstruction.serialization import to_portable_json
from ai_friend.skills.models import RuntimeCapability


def synthetic_graph() -> ReconstructionGraph:
    source = SourceReference("src-a", "Invented micro-scene", "fixture://synthetic/a", "text/plain", approved=True)
    units = tuple(
        SourceUnit(
            f"unit-{index}", source.id, text, f"line:{index}",
            grounding=SourceUnitGrounding.EXACT_TEXT,
            integrity_hash=f"sha256:synthetic-{index}",
        )
        for index, text in enumerate((
            "Mira repairs a cracked signal lamp.",
            "Mira gives the repaired lamp to the night guard.",
            "After moving workshops, Mira asks for a checklist before starting.",
        ), start=1)
    )
    observations = tuple(
        ObservationRecord(
            f"obs-{index}", content, Lineage(source_unit_ids=(f"unit-{index}",)),
        )
        for index, content in enumerate((
            "Mira completes a lamp repair.",
            "Mira transfers the working lamp to its user.",
            "Mira requests a checklist in the new workshop.",
        ), start=1)
    )
    events = tuple(
        EventRecord(
            f"event-{index}", description,
            Lineage(parent_artifact_ids=(f"obs-{index}",)),
            TemporalScope(label=f"synthetic-event-{index}"),
            participants=("Mira",), objective_facts=(description,),
            character_accessible_information=(description,),
        )
        for index, description in enumerate((
            "A lamp is repaired.", "The repaired lamp is delivered.", "A checklist is requested after relocation."
        ), start=1)
    )
    evidence = tuple(
        EvidenceRecord(
            f"evidence-{index}", statement, EvidenceStance.SUPPORTS,
            Lineage(parent_artifact_ids=(f"event-{index}",)),
        )
        for index, statement in enumerate((
            "The repair demonstrates bounded tool use.",
            "The handoff supports responsibility during period one.",
            "The later request supports a candidate planning adaptation.",
        ), start=1)
    )
    periods = (
        PeriodDefinition("period-1", 1, TemporalScope(label="old-workshop"), BoundaryStatus.CONFIRMED, "initial setting", 1),
        PeriodDefinition("period-2", 2, TemporalScope(label="new-workshop"), BoundaryStatus.CANDIDATE, "workshop relocation", 2),
    )
    assignments = (
        PeriodAssignment("assign-1", "event-1", "period-1", "occurred before relocation"),
        PeriodAssignment("assign-2", "event-2", "period-1", "occurred before relocation"),
        PeriodAssignment("assign-3", "event-3", "period-2", "candidate post-relocation state"),
    )
    bundle = ReconstructionBundle(
        "synthetic-mira", 1, sources=(source,), source_units=units,
        observations=observations, events=events, evidence=evidence,
        period_definitions=periods, period_assignments=assignments,
        metadata={"schema_version": "0.0.8", "character_version": "synthetic-1"},
    )
    p1 = PeriodCharacterState(
        "state-1", "period-1", periods[0].temporal_scope, KnowledgeBoundary(1),
        PeriodDomains(
            personality=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Shows task follow-through in this period.",), ("event-2",), ("evidence-2",)),
            motivation=DomainEntry(DomainEvidenceState.OBSERVED, ("Completes and delivers the repair.",), ("event-2",), ("evidence-2",)),
            emotion=DomainEntry(DomainEvidenceState.INSUFFICIENT_EVIDENCE),
        ),
        supporting_event_ids=("event-1", "event-2"), supporting_evidence_ids=("evidence-1", "evidence-2"),
    )
    p2 = PeriodCharacterState(
        "state-2", "period-2", periods[1].temporal_scope, KnowledgeBoundary(2),
        PeriodDomains(
            personality=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Uses explicit planning support in the new setting.",), ("event-3",), ("evidence-3",)),
            growth=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Planning may be adapting after relocation.",), ("event-3",), ("evidence-3",), "Only one later event."),
        ),
        supporting_event_ids=("event-3",), supporting_evidence_ids=("evidence-3",),
        uncertainty="Candidate period boundary and bounded change.",
    )
    development = DevelopmentRecord(
        "development-1", "Planning behavior may have become more explicit after relocation.",
        (p1.id, p2.id), Lineage(parent_artifact_ids=("evidence-2", "evidence-3")),
        confidence="limited", change_resistance=ChangeResistance("unresolved", "Two periods do not establish resistance."),
        causal_hypotheses=(CausalHypothesis(
            "Relocation may have encouraged explicit planning.", ("evidence-3",), ("evidence-2",),
            ("The checklist request may be situational.",), "Causal attribution is unresolved.",
        ),), status=ArtifactStatus.UNRESOLVED,
    )
    memory = MemoryRecord(
        "memory-2", "Remembers delivering the repaired lamp.", event_ids=("event-2",),
        period_id="period-1", remembered_content="The lamp reached the guard.",
        subjective_meaning="The repair mattered because it was used.",
    )
    decisions = (
        MemoryFormationDecision("event-1", MemoryFormationOutcome.DO_NOT_PERSIST, "Routine action."),
        MemoryFormationDecision("event-2", MemoryFormationOutcome.PERSIST, "Meaningful handoff.", "memory-2"),
    )
    skill_evidence = SkillEvidence("skill-evidence-1", ("event-1",), ("evidence-1",), ("Repairs one signal lamp.",))
    skill_profile = CharacterSkillProfile(
        "skill-profile-1", "lamp-repair", SkillAcquisitionOrigin.CANON_SUPPORTED,
        "single demonstrated repair", (skill_evidence.id,), "period-1", ("No evidence of expert diagnosis.",),
    )
    compiled = CompiledCharacterState(
        "compiled-1", "0.0.8", "synthetic-1", p2.id, (p1.id, p2.id),
        (CompiledStateEntry("Uses explicit planning in the current candidate period.", (p2.id,), (development.id,), ("evidence-3",)),),
        (development.id,), ("Planning persistence remains unresolved.",),
    )
    return ReconstructionGraph(bundle, (p1, p2), (development,), (memory,), decisions, (skill_evidence,), (skill_profile,), (compiled,))


def issue_codes(graph: ReconstructionGraph) -> set[str]:
    return {issue.code for issue in validate_reconstruction_graph(graph).issues}


def test_source_unit_preserves_source_grounding() -> None:
    graph = synthetic_graph()
    assert graph.bundle.source_units[0].grounding is SourceUnitGrounding.EXACT_TEXT
    invalid = replace(graph.bundle.source_units[0], grounding=None)
    assert "unmarked_source_unit" in issue_codes(replace(graph, bundle=replace(graph.bundle, source_units=(invalid, *graph.bundle.source_units[1:]))))


def test_event_is_single_source_of_truth_and_can_influence_multiple_domains() -> None:
    graph = synthetic_graph()
    event_id = "event-2"
    assert sum(event.id == event_id for event in graph.bundle.events) == 1
    state = graph.period_states[0]
    assert event_id in state.domains.personality.event_ids
    assert event_id in state.domains.motivation.event_ids


def test_period_state_has_eight_domain_slots_and_allows_missing_evidence() -> None:
    state = synthetic_graph().period_states[0]
    assert {domain.value for domain in TraitDomain} == set(PeriodDomains.__dataclass_fields__)
    assert state.domains.emotion.state is DomainEvidenceState.INSUFFICIENT_EVIDENCE


def test_period_cannot_use_future_knowledge() -> None:
    graph = synthetic_graph()
    earlier = replace(graph.period_states[0], supporting_event_ids=("event-1", "event-3"))
    assert "future_knowledge" in issue_codes(replace(graph, period_states=(earlier, graph.period_states[1])))


def test_development_requires_multiple_periods_and_causal_uncertainty() -> None:
    graph = synthetic_graph()
    development = replace(graph.developments[0], period_state_ids=("state-1",))
    assert "development_without_multiple_periods" in issue_codes(replace(graph, developments=(development,)))
    hypothesis = replace(graph.developments[0].causal_hypotheses[0], uncertainty=None, alternative_hypotheses=(), counterevidence_ids=())
    development = replace(graph.developments[0], causal_hypotheses=(hypothesis,))
    codes = issue_codes(replace(graph, developments=(development,)))
    assert {"incomplete_causal_hypothesis", "causal_hypothesis_without_alternative"} <= codes


def test_confidence_is_not_change_resistance() -> None:
    development = synthetic_graph().developments[0]
    assert development.confidence == "limited"
    assert development.change_resistance is not None
    assert development.change_resistance.value == "unresolved"


def test_memory_references_event_without_copying_and_can_be_absent() -> None:
    graph = synthetic_graph()
    assert graph.memories[0].event_ids == ("event-2",)
    assert "event" not in graph.memories[0].metadata
    assert any(item.event_id == "event-1" and item.outcome is MemoryFormationOutcome.DO_NOT_PERSIST for item in graph.memory_decisions)


def test_skill_profile_requires_evidence_and_runtime_cannot_rewrite_it() -> None:
    graph = synthetic_graph()
    invalid = replace(graph.skill_profiles[0], skill_evidence_ids=())
    assert "skill_profile_without_evidence" in issue_codes(replace(graph, skill_profiles=(invalid,)))
    canonical = graph.skill_profiles[0]
    runtime_capability = RuntimeCapability(canonical.skill_id, "diagnostic-helper", True, "synthetic-tool")
    assert runtime_capability.enabled and canonical.canonical_proficiency == "single demonstrated repair"


def test_compiled_state_traces_to_period_state() -> None:
    graph = synthetic_graph()
    assert graph.compiled_states[0].entries[0].period_state_ids == ("state-2",)
    invalid_entry = replace(graph.compiled_states[0].entries[0], period_state_ids=())
    invalid = replace(graph.compiled_states[0], entries=(invalid_entry,))
    assert "compiled_entry_without_period" in issue_codes(replace(graph, compiled_states=(invalid,)))


def test_reference_note_is_not_canonical_evidence() -> None:
    graph = synthetic_graph()
    note = replace(graph.bundle.sources[0], metadata={"source_role": "reference_note"})
    assert "reference_note_as_source" in issue_codes(replace(graph, bundle=replace(graph.bundle, sources=(note,))))


def test_end_to_end_synthetic_reconstruction_and_serialization() -> None:
    graph = synthetic_graph()
    report = validate_reconstruction_graph(graph)
    assert report.is_valid, report.issues
    serialized = to_portable_json(graph.compiled_states[0], schema_version="0.0.8", artifact_version="synthetic-1")
    assert serialized == to_portable_json(graph.compiled_states[0], schema_version="0.0.8", artifact_version="synthetic-1")
    assert '"schema_version": "0.0.8"' in serialized
