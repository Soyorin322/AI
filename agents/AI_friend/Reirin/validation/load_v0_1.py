"""Reload persisted Reirin v0.1 JSON into authoritative Aiko dataclasses."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_friend.character.reconstruction import (
    CausalHypothesis, CharacterSkillProfile, ChangeResistance, CompiledCharacterState,
    CompiledStateEntry, DevelopmentRecord, DomainEntry, DomainEvidenceState,
    HistoricalAdaptation, KnowledgeBoundary, PeriodCharacterState, PeriodDomains,
    SkillAcquisitionOrigin, SkillEvidence,
)
from ai_friend.memory.models import MemoryFormationDecision, MemoryFormationOutcome, MemoryRecord
from ai_friend.reconstruction.hardening import ReconstructionGraph
from ai_friend.reconstruction.models import (
    ArtifactStatus, BoundaryStatus, EventRecord, EvidenceRecord, EvidenceStance,
    ObservationRecord, PeriodAssignment, PeriodDefinition, ReconstructionBundle,
    SourceReference, SourceUnit, SourceUnitGrounding, TemporalScope,
)
from ai_friend.reconstruction.provenance import Lineage


ROOT = Path(__file__).resolve().parents[1]


def _artifact(relative: str) -> Any:
    data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.0.8" or data.get("artifact_version") != "Reirin-v0.1":
        raise ValueError(f"unexpected serialization envelope: {relative}")
    return data["artifact"]


def _scope(data: dict[str, Any] | None) -> TemporalScope | None:
    return TemporalScope(**data) if data is not None else None


def _lineage(data: dict[str, Any]) -> Lineage:
    return Lineage(tuple(data.get("source_ids", ())), tuple(data.get("source_unit_ids", ())), tuple(data.get("parent_artifact_ids", ())))


def _domain(data: dict[str, Any]) -> DomainEntry:
    return DomainEntry(
        DomainEvidenceState(data["state"]), tuple(data.get("statements", ())),
        tuple(data.get("event_ids", ())), tuple(data.get("evidence_ids", ())), data.get("uncertainty"),
    )


def load_graph() -> ReconstructionGraph:
    manifest = json.loads((ROOT / "reconstruction/manifests/reconstruction_v0.1_manifest.json").read_text(encoding="utf-8"))
    raw_source = manifest["source_reference"]
    source = SourceReference(
        raw_source["id"], raw_source["title"], raw_source["locator"], raw_source["media_type"],
        raw_source.get("metadata", {}), raw_source["approved"],
    )
    units = tuple(
        SourceUnit(
            item["id"], item["source_id"], item["content"], item.get("locator"), _scope(item.get("temporal_scope")),
            item.get("metadata", {}), SourceUnitGrounding(item["grounding"]) if item.get("grounding") else None,
            item.get("integrity_hash"),
        ) for item in _artifact("reconstruction/source_units/source_units_v0.1.json")
    )
    observations = tuple(
        ObservationRecord(item["id"], item["content"], _lineage(item["lineage"]), _scope(item.get("temporal_scope")), item.get("metadata", {}))
        for item in _artifact("reconstruction/observations/observations_v0.1.json")
    )
    events = tuple(
        EventRecord(
            item["id"], item["description"], _lineage(item["lineage"]), _scope(item.get("temporal_scope")), item.get("metadata", {}),
            tuple(item.get("participants", ())), tuple(item.get("objective_facts", ())),
            tuple(item.get("character_accessible_information", ())), tuple(item.get("explicit_statements", ())),
            tuple(item.get("observed_behaviors", ())), item.get("outcome"), item.get("uncertainty"),
        ) for item in _artifact("reconstruction/events/events_v0.1.json")
    )
    evidence = tuple(
        EvidenceRecord(
            item["id"], item["content"], EvidenceStance(item["stance"]), _lineage(item["lineage"]),
            _scope(item.get("temporal_scope")), item.get("metadata", {}),
        ) for item in _artifact("reconstruction/evidence/evidence_v0.1.json")
    )
    periods = tuple(
        PeriodDefinition(
            item["id"], item["order"], _scope(item["temporal_scope"]), BoundaryStatus(item["boundary_status"]),
            item["boundary_reason"], item["knowledge_boundary_order"], item.get("metadata", {}),
        ) for item in _artifact("reconstruction/periods/period_definitions_v0.1.json")
    )
    assignments = tuple(
        PeriodAssignment(item["id"], item["event_id"], item["period_id"], item["reason"], BoundaryStatus(item["status"]), item.get("metadata", {}))
        for item in _artifact("reconstruction/periods/period_assignments_v0.1.json")
    )
    states = tuple(
        PeriodCharacterState(
            item["id"], item["period_id"], _scope(item["temporal_scope"]),
            KnowledgeBoundary(
                item["knowledge_boundary"]["as_of_period_order"],
                tuple(item["knowledge_boundary"].get("accessible_fact_ids", ())),
                tuple(item["knowledge_boundary"].get("excluded_fact_ids", ())),
            ),
            PeriodDomains(**{name: _domain(value) for name, value in item["domains"].items()}),
            tuple(item.get("supporting_event_ids", ())), tuple(item.get("supporting_evidence_ids", ())),
            ArtifactStatus(item["status"]), item.get("uncertainty"),
        ) for item in _artifact("reconstruction/periods/period_states_v0.1.json")
    )
    developments = tuple(
        DevelopmentRecord(
            item["id"], item["statement"], tuple(item["period_state_ids"]), _lineage(item["lineage"]),
            item.get("confidence"),
            ChangeResistance(**item["change_resistance"]) if item.get("change_resistance") else None,
            tuple(HistoricalAdaptation(h["statement"], tuple(h["period_ids"]), tuple(h.get("evidence_ids", ())), h.get("uncertainty")) for h in item.get("historical_adaptations", ())),
            tuple(CausalHypothesis(h["statement"], tuple(h["supporting_evidence_ids"]), tuple(h.get("counterevidence_ids", ())), tuple(h.get("alternative_hypotheses", ())), h.get("uncertainty")) for h in item.get("causal_hypotheses", ())),
            (), (), _scope(item.get("temporal_scope")), ArtifactStatus(item["status"]),
        ) for item in _artifact("reconstruction/development/development_v0.1.json")
    )
    decisions = tuple(
        MemoryFormationDecision(item["event_id"], MemoryFormationOutcome(item["outcome"]), item["reason"], item.get("memory_id"))
        for item in _artifact("memory/records/memory_decisions_v0.1.json")
    )
    memories = tuple(
        MemoryRecord(
            item["id"], item["content"], datetime.fromisoformat(item["timestamp"]), item.get("metadata", {}),
            tuple(item.get("event_ids", ())), item.get("period_id"), item.get("remembered_content"),
            item.get("subjective_meaning"), item.get("affective_trace"), item.get("uncertainty"),
            tuple(item.get("accessible_fact_ids", ())),
        ) for item in _artifact("memory/records/memories_v0.1.json")
    )
    skill_evidence = tuple(
        SkillEvidence(item["id"], tuple(item.get("event_ids", ())), tuple(item.get("evidence_ids", ())), tuple(item.get("demonstrated_behaviors", ())), tuple(item.get("explicit_training", ())))
        for item in _artifact("character/skill_profile/skill_evidence_v0.1.json")
    )
    skill_profiles = tuple(
        CharacterSkillProfile(
            item["id"], item["skill_id"], SkillAcquisitionOrigin(item["origin"]), item["canonical_proficiency"],
            tuple(item["skill_evidence_ids"]), item.get("period_id"), tuple(item.get("limitations", ())), item.get("uncertainty"),
        ) for item in _artifact("character/skill_profile/skill_profile_v0.1.json")
    )
    compiled = tuple(
        CompiledCharacterState(
            item["id"], item["schema_version"], item["character_version"], item["current_period_state_id"],
            tuple(item["historical_period_state_ids"]),
            tuple(CompiledStateEntry(e["statement"], tuple(e["period_state_ids"]), tuple(e.get("development_ids", ())), tuple(e.get("evidence_ids", ()))) for e in item["entries"]),
            tuple(item.get("development_ids", ())), tuple(item.get("unresolved_items", ())),
        ) for item in _artifact("character/compiled/compiled_character_state_v0.1.json")
    )
    bundle = ReconstructionBundle(
        "reirin-reconstruction", 1, (source,), units, observations, events, evidence, (), (), None,
        {"schema_version": "0.0.8", "character_id": "Reirin", "reconstruction_version": "0.1", "source_scope": "first-three-chapters-only"},
        periods, assignments,
    )
    return ReconstructionGraph(bundle, states, developments, memories, decisions, skill_evidence, skill_profiles, compiled)
