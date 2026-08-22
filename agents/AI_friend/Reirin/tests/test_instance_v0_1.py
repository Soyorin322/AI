import hashlib
import json
from dataclasses import fields
from pathlib import Path

from ai_friend.character.reconstruction import PeriodDomains
from ai_friend.reconstruction.hardening import validate_reconstruction_graph
from ai_friend.reconstruction.models import SourceUnitGrounding

from validation.load_v0_1 import load_graph


def test_persisted_reirin_v0_1_passes_aiko_validation() -> None:
    graph = load_graph()
    assert validate_reconstruction_graph(graph).is_valid
    assert graph.bundle.sources[0].approved
    assert all(unit.grounding is SourceUnitGrounding.EXACT_TEXT for unit in graph.bundle.source_units)
    assert all(unit.integrity_hash == f"sha256:{hashlib.sha256(unit.content.encode('utf-8')).hexdigest()}" for unit in graph.bundle.source_units)
    observation_ids = {item.id for item in graph.bundle.observations}
    assert all(set(event.lineage.parent_artifact_ids) <= observation_ids for event in graph.bundle.events)
    assert len(graph.bundle.period_assignments) == len(graph.bundle.events)
    assert all(len(fields(state.domains)) == 8 for state in graph.period_states)
    assert all(len(record.period_state_ids) >= 2 for record in graph.developments)
    assert all(memory.event_ids for memory in graph.memories)
    assert all(profile.skill_evidence_ids for profile in graph.skill_profiles)
    assert all(entry.period_state_ids for state in graph.compiled_states for entry in state.entries)
    manifest = json.loads((Path(__file__).resolve().parents[1] / "reconstruction/manifests/reconstruction_v0.1_manifest.json").read_text(encoding="utf-8"))
    assert manifest["validation_error_count"] == 0


def test_compiled_entries_reach_the_single_approved_source() -> None:
    graph = load_graph()
    states = {item.id: item for item in graph.period_states}
    events = {item.id: item for item in graph.bundle.events}
    observations = {item.id: item for item in graph.bundle.observations}
    units = {item.id: item for item in graph.bundle.source_units}
    evidence = {item.id: item for item in graph.bundle.evidence}

    def event_reaches_source(event_id: str) -> bool:
        event = events[event_id]
        return any(
            units[unit_id].source_id == "source-v1-first-three"
            for observation_id in event.lineage.parent_artifact_ids
            for unit_id in observations[observation_id].lineage.source_unit_ids
        )

    for compiled in graph.compiled_states:
        for entry in compiled.entries:
            linked_states = [states[state_id] for state_id in entry.period_state_ids]
            linked_event_ids = {event_id for state in linked_states for event_id in state.supporting_event_ids}
            linked_event_ids.update(
                parent_id
                for evidence_id in entry.evidence_ids
                for parent_id in evidence[evidence_id].lineage.parent_artifact_ids
                if parent_id in events
            )
            assert linked_event_ids
            assert all(event_reaches_source(event_id) for event_id in linked_event_ids)


def test_persisted_knowledge_boundary_excludes_private_lily_event() -> None:
    graph = load_graph()
    state = next(item for item in graph.period_states if item.period_id == "period-003")
    assert "fact-lily-private-inducement" in state.knowledge_boundary.excluded_fact_ids
    assert all("event-012" not in memory.event_ids for memory in graph.memories)
