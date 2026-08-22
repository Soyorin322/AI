"""Validate the persisted Reirin v0.1 instance, not the builder's memory graph."""

import json
from pathlib import Path

from ai_friend.reconstruction.hardening import validate_reconstruction_graph

from load_v0_1 import load_graph


def main() -> None:
    graph = load_graph()
    report = validate_reconstruction_graph(graph)
    report.raise_for_errors()
    manifest_path = Path(__file__).resolve().parents[1] / "reconstruction/manifests/reconstruction_v0.1_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["validation_status"] = "passed: persisted JSON reloaded into Aiko dataclasses; 0 validation errors"
    manifest["validation_error_count"] = 0
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "valid persisted Reirin v0.1: "
        f"sources={len(graph.bundle.sources)} units={len(graph.bundle.source_units)} "
        f"observations={len(graph.bundle.observations)} events={len(graph.bundle.events)} "
        f"evidence={len(graph.bundle.evidence)} periods={len(graph.bundle.period_definitions)} "
        f"assignments={len(graph.bundle.period_assignments)} states={len(graph.period_states)} "
        f"memory_decisions={len(graph.memory_decisions)} memories={len(graph.memories)} "
        f"skill_evidence={len(graph.skill_evidence)} skill_profiles={len(graph.skill_profiles)} "
        f"developments={len(graph.developments)} compiled={len(graph.compiled_states)}"
    )


if __name__ == "__main__":
    main()
