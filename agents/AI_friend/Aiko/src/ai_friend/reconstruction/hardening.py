"""Task 005 cross-stage graph and structural validation.

This module validates reference direction and abstention states. It deliberately
does not score psychology, confidence, change resistance, or consolidation.
"""

from dataclasses import dataclass

from ai_friend.character.reconstruction import (
    CharacterSkillProfile,
    CompiledCharacterState,
    DevelopmentRecord,
    DomainEvidenceState,
    PeriodCharacterState,
    SkillEvidence,
)
from ai_friend.memory.models import MemoryFormationDecision, MemoryFormationOutcome, MemoryRecord
from ai_friend.reconstruction.models import (
    EvidenceRecord,
    EventRecord,
    ObservationRecord,
    PeriodAssignment,
    PeriodDefinition,
    ReconstructionBundle,
    SourceUnitGrounding,
)
from ai_friend.reconstruction.validation import ValidationIssue, ValidationReport, validate_bundle


@dataclass(frozen=True, slots=True)
class ReconstructionGraph:
    bundle: ReconstructionBundle
    period_states: tuple[PeriodCharacterState, ...] = ()
    developments: tuple[DevelopmentRecord, ...] = ()
    memories: tuple[MemoryRecord, ...] = ()
    memory_decisions: tuple[MemoryFormationDecision, ...] = ()
    skill_evidence: tuple[SkillEvidence, ...] = ()
    skill_profiles: tuple[CharacterSkillProfile, ...] = ()
    compiled_states: tuple[CompiledCharacterState, ...] = ()


def validate_reconstruction_graph(graph: ReconstructionGraph) -> ValidationReport:
    issues = list(validate_bundle(graph.bundle).issues)
    _validate_events(graph.bundle, issues)
    periods = _validate_periods(graph.bundle.period_definitions, graph.bundle.period_assignments, graph.bundle.events, issues)
    _validate_period_states(graph, periods, issues)
    _validate_development(graph, issues)
    _validate_memories(graph, issues)
    _validate_skills(graph, issues)
    _validate_compiled(graph, issues)
    _validate_cross_graph_ids(graph, issues)
    return ValidationReport(tuple(issues))


def _issue(issues: list[ValidationIssue], code: str, message: str, artifact_id: str) -> None:
    issues.append(ValidationIssue(code, message, artifact_id))


def _validate_events(bundle: ReconstructionBundle, issues: list[ValidationIssue]) -> None:
    observations = {item.id for item in bundle.observations}
    for event in bundle.events:
        if event.temporal_scope is None:
            _issue(issues, "event_without_temporal_scope", f"event {event.id} lacks temporal scope", event.id)
        if not any(parent in observations for parent in event.lineage.parent_artifact_ids):
            _issue(issues, "event_without_observation", f"event {event.id} has no observation parent", event.id)
        if any(parent not in observations for parent in event.lineage.parent_artifact_ids):
            _issue(issues, "invalid_event_parent", f"event {event.id} has a non-Observation parent", event.id)
        if "persistent_trait" in event.metadata or "canonical_trait" in event.metadata:
            _issue(issues, "event_declares_trait", f"event {event.id} declares persistent character state", event.id)


def _validate_periods(
    periods: tuple[PeriodDefinition, ...],
    assignments: tuple[PeriodAssignment, ...],
    events: tuple[EventRecord, ...],
    issues: list[ValidationIssue],
) -> dict[str, PeriodDefinition]:
    period_map = {item.id: item for item in periods}
    event_ids = {item.id for item in events}
    orders = [item.order for item in periods]
    if any(order < 1 for order in orders) or len(set(orders)) != len(orders):
        _issue(issues, "invalid_period_order", "period orders must be unique positive integers", "periods")
    assigned_events: set[str] = set()
    for assignment in assignments:
        if assignment.event_id not in event_ids:
            _issue(issues, "missing_period_event", f"assignment {assignment.id} references missing event", assignment.id)
        if assignment.period_id not in period_map:
            _issue(issues, "missing_assignment_period", f"assignment {assignment.id} references missing period", assignment.id)
        if assignment.event_id in assigned_events:
            _issue(issues, "duplicate_event_assignment", f"event {assignment.event_id} is assigned more than once", assignment.id)
        assigned_events.add(assignment.event_id)
    return period_map


def _domain_entries(state: PeriodCharacterState):
    return (
        state.domains.personality, state.domains.physical, state.domains.motivation,
        state.domains.backstory, state.domains.emotion, state.domains.relationships,
        state.domains.growth, state.domains.conflict,
    )


def _validate_period_states(graph: ReconstructionGraph, periods: dict[str, PeriodDefinition], issues: list[ValidationIssue]) -> None:
    event_ids = {item.id for item in graph.bundle.events}
    evidence_ids = {item.id for item in graph.bundle.evidence}
    assignment_period = {item.event_id: item.period_id for item in graph.bundle.period_assignments}
    absent = {
        DomainEvidenceState.UNKNOWN, DomainEvidenceState.UNCHANGED,
        DomainEvidenceState.INSUFFICIENT_EVIDENCE, DomainEvidenceState.NOT_APPLICABLE,
    }
    for state in graph.period_states:
        period = periods.get(state.period_id)
        if period is None:
            _issue(issues, "missing_state_period", f"period state {state.id} references missing period", state.id)
            continue
        if state.knowledge_boundary.as_of_period_order > period.knowledge_boundary_order:
            _issue(issues, "future_knowledge", f"period state {state.id} exceeds its knowledge boundary", state.id)
        for event_id in state.supporting_event_ids:
            if event_id not in event_ids:
                _issue(issues, "missing_state_event", f"period state {state.id} references missing event {event_id}", state.id)
            assigned = periods.get(assignment_period.get(event_id, ""))
            if assigned and assigned.order > state.knowledge_boundary.as_of_period_order:
                _issue(issues, "future_knowledge", f"period state {state.id} uses later event {event_id}", state.id)
        for evidence_id in state.supporting_evidence_ids:
            if evidence_id not in evidence_ids:
                _issue(issues, "missing_state_evidence", f"period state {state.id} references missing evidence {evidence_id}", state.id)
        for entry in _domain_entries(state):
            if entry.state in absent and (entry.statements or entry.event_ids or entry.evidence_ids):
                _issue(issues, "filled_absent_domain", f"period state {state.id} fills an abstaining domain", state.id)
            if entry.state not in absent and not (entry.event_ids or entry.evidence_ids):
                _issue(issues, "ungrounded_domain", f"period state {state.id} has an ungrounded domain entry", state.id)
            for event_id in entry.event_ids:
                if event_id not in event_ids:
                    _issue(issues, "missing_domain_event", f"period state {state.id} references missing event {event_id}", state.id)
                assigned = periods.get(assignment_period.get(event_id, ""))
                if assigned and assigned.order > state.knowledge_boundary.as_of_period_order:
                    _issue(issues, "future_knowledge", f"period state {state.id} domain uses later event {event_id}", state.id)
            for evidence_id in entry.evidence_ids:
                if evidence_id not in evidence_ids:
                    _issue(issues, "missing_domain_evidence", f"period state {state.id} references missing evidence {evidence_id}", state.id)


def _validate_development(graph: ReconstructionGraph, issues: list[ValidationIssue]) -> None:
    states = {item.id for item in graph.period_states}
    evidence = {item.id for item in graph.bundle.evidence}
    for record in graph.developments:
        if len(set(record.period_state_ids)) < 2:
            _issue(issues, "development_without_multiple_periods", f"development {record.id} needs multiple period states", record.id)
        for state_id in record.period_state_ids:
            if state_id not in states:
                _issue(issues, "missing_development_period", f"development {record.id} references missing state {state_id}", record.id)
        if not record.lineage.parent_artifact_ids:
            _issue(issues, "development_without_lineage", f"development {record.id} lacks lower-level lineage", record.id)
        for parent_id in record.lineage.parent_artifact_ids:
            if parent_id not in evidence and parent_id not in states:
                _issue(issues, "invalid_development_parent", f"development {record.id} has invalid parent {parent_id}", record.id)
        for hypothesis in record.causal_hypotheses:
            if not hypothesis.supporting_evidence_ids or not hypothesis.uncertainty:
                _issue(issues, "incomplete_causal_hypothesis", f"development {record.id} has an unsupported or certainty-free causal hypothesis", record.id)
            if not (hypothesis.alternative_hypotheses or hypothesis.counterevidence_ids):
                _issue(issues, "causal_hypothesis_without_alternative", f"development {record.id} lacks alternatives/counterevidence", record.id)
            for evidence_id in (*hypothesis.supporting_evidence_ids, *hypothesis.counterevidence_ids):
                if evidence_id not in evidence:
                    _issue(issues, "missing_causal_evidence", f"development {record.id} references missing evidence {evidence_id}", record.id)


def _validate_memories(graph: ReconstructionGraph, issues: list[ValidationIssue]) -> None:
    event_ids = {item.id for item in graph.bundle.events}
    memories = {item.id for item in graph.memories}
    periods = {item.id: item for item in graph.bundle.period_definitions}
    assigned_period = {item.event_id: item.period_id for item in graph.bundle.period_assignments}
    events = {item.id: item for item in graph.bundle.events}
    for memory in graph.memories:
        if not memory.event_ids:
            _issue(issues, "memory_without_event", f"memory {memory.id} has no Event reference", memory.id)
        if memory.period_id is not None and memory.period_id not in periods:
            _issue(issues, "missing_memory_period", f"memory {memory.id} references missing period", memory.id)
        for event_id in memory.event_ids:
            if event_id not in event_ids:
                _issue(issues, "missing_memory_event", f"memory {memory.id} references missing event {event_id}", memory.id)
            memory_period = periods.get(memory.period_id or "")
            event_period = periods.get(assigned_period.get(event_id, ""))
            if memory_period and event_period and event_period.order > memory_period.order:
                _issue(issues, "future_memory_event", f"memory {memory.id} references a later-period event", memory.id)
            inaccessible = set(events.get(event_id).metadata.get("inaccessible_fact_ids", ())) if event_id in events else set()
            if inaccessible.intersection(memory.accessible_fact_ids):
                _issue(issues, "inaccessible_memory_fact", f"memory {memory.id} includes inaccessible facts", memory.id)
        if any(key in memory.metadata for key in ("event", "objective_event", "objective_facts")):
            _issue(issues, "duplicated_event_in_memory", f"memory {memory.id} embeds Event data", memory.id)
    for decision in graph.memory_decisions:
        if decision.event_id not in event_ids:
            _issue(issues, "missing_decision_event", f"memory decision references missing event {decision.event_id}", decision.event_id)
        if decision.outcome is MemoryFormationOutcome.PERSIST and decision.memory_id not in memories:
            _issue(issues, "missing_decision_memory", f"persist decision for {decision.event_id} lacks a MemoryRecord", decision.event_id)
        if decision.outcome is MemoryFormationOutcome.DO_NOT_PERSIST and decision.memory_id is not None:
            _issue(issues, "nonpersistent_decision_has_memory", f"non-persist decision for {decision.event_id} names a memory", decision.event_id)


def _validate_skills(graph: ReconstructionGraph, issues: list[ValidationIssue]) -> None:
    event_ids = {item.id for item in graph.bundle.events}
    evidence_ids = {item.id for item in graph.bundle.evidence}
    skill_evidence = {item.id: item for item in graph.skill_evidence}
    periods = {item.id for item in graph.bundle.period_definitions}
    for item in graph.skill_evidence:
        if not item.event_ids and not item.evidence_ids:
            _issue(issues, "ungrounded_skill_evidence", f"skill evidence {item.id} lacks Event/Evidence refs", item.id)
        for ref in item.event_ids:
            if ref not in event_ids:
                _issue(issues, "missing_skill_event", f"skill evidence {item.id} references missing event {ref}", item.id)
        for ref in item.evidence_ids:
            if ref not in evidence_ids:
                _issue(issues, "missing_skill_evidence_ref", f"skill evidence {item.id} references missing evidence {ref}", item.id)
    for profile in graph.skill_profiles:
        if not profile.skill_evidence_ids:
            _issue(issues, "skill_profile_without_evidence", f"skill profile {profile.id} lacks evidence", profile.id)
        for ref in profile.skill_evidence_ids:
            if ref not in skill_evidence:
                _issue(issues, "missing_skill_profile_evidence", f"skill profile {profile.id} references missing skill evidence {ref}", profile.id)
        if profile.period_id is not None and profile.period_id not in periods:
            _issue(issues, "missing_skill_period", f"skill profile {profile.id} references missing period", profile.id)


def _validate_compiled(graph: ReconstructionGraph, issues: list[ValidationIssue]) -> None:
    states = {item.id for item in graph.period_states}
    developments = {item.id for item in graph.developments}
    for compiled in graph.compiled_states:
        if compiled.current_period_state_id not in states:
            _issue(issues, "missing_compiled_period", f"compiled state {compiled.id} lacks current period state", compiled.id)
        if not compiled.schema_version or not compiled.character_version:
            _issue(issues, "missing_compiled_version", f"compiled state {compiled.id} lacks explicit versions", compiled.id)
        for entry in compiled.entries:
            if not entry.period_state_ids:
                _issue(issues, "compiled_entry_without_period", f"compiled state {compiled.id} has an untraceable entry", compiled.id)
            for ref in entry.period_state_ids:
                if ref not in states:
                    _issue(issues, "missing_compiled_entry_period", f"compiled state {compiled.id} references missing state {ref}", compiled.id)
            for ref in entry.development_ids:
                if ref not in developments:
                    _issue(issues, "missing_compiled_development", f"compiled state {compiled.id} references missing development {ref}", compiled.id)
        for ref in compiled.development_ids:
            if ref not in developments:
                _issue(issues, "missing_compiled_development", f"compiled state {compiled.id} references missing development {ref}", compiled.id)


def _validate_cross_graph_ids(graph: ReconstructionGraph, issues: list[ValidationIssue]) -> None:
    ids = [
        *(item.id for item in graph.bundle.sources), *(item.id for item in graph.bundle.source_units),
        *(item.id for item in graph.bundle.observations), *(item.id for item in graph.bundle.events),
        *(item.id for item in graph.bundle.evidence), *(item.id for item in graph.bundle.claims),
        *(item.id for item in graph.bundle.snapshots), *(item.id for item in graph.bundle.period_definitions),
        *(item.id for item in graph.bundle.period_assignments),
        *(item.id for item in graph.period_states), *(item.id for item in graph.developments),
        *(item.id for item in graph.memories), *(item.id for item in graph.skill_evidence),
        *(item.id for item in graph.skill_profiles), *(item.id for item in graph.compiled_states),
    ]
    for artifact_id in sorted({item for item in ids if ids.count(item) > 1}):
        _issue(issues, "duplicate_cross_stage_id", f"duplicate cross-stage id: {artifact_id}", artifact_id)
