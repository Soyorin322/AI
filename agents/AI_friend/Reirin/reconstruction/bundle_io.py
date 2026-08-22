"""Deterministic JSON mapping for the Reirin instance and Aiko contracts."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ai_friend.reconstruction.models import (
    ArtifactStatus,
    CharacterClaim,
    CharacterStateSnapshot,
    EventRecord,
    EvidenceRecord,
    EvidenceStance,
    ObservationRecord,
    ReconstructionBundle,
    SourceReference,
    SourceUnit,
    StatusTransition,
    TemporalScope,
)
from ai_friend.reconstruction.provenance import Lineage


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value


def bundle_to_dict(bundle: ReconstructionBundle) -> dict[str, Any]:
    return _encode(asdict(bundle))


def write_bundle(bundle: ReconstructionBundle, path: Path) -> None:
    path.write_text(
        json.dumps(bundle_to_dict(bundle), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _temporal(data: dict[str, Any] | None) -> TemporalScope | None:
    return TemporalScope(**data) if data is not None else None


def _lineage(data: dict[str, Any]) -> Lineage:
    return Lineage(
        source_ids=tuple(data.get("source_ids", ())),
        source_unit_ids=tuple(data.get("source_unit_ids", ())),
        parent_artifact_ids=tuple(data.get("parent_artifact_ids", ())),
    )


def load_bundle(path: Path) -> ReconstructionBundle:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = tuple(SourceReference(**item) for item in data["sources"])
    units = tuple(
        SourceUnit(
            id=item["id"], source_id=item["source_id"], content=item["content"],
            locator=item.get("locator"), temporal_scope=_temporal(item.get("temporal_scope")),
            metadata=item.get("metadata", {}),
        )
        for item in data["source_units"]
    )
    observations = tuple(
        ObservationRecord(
            id=item["id"], content=item["content"], lineage=_lineage(item["lineage"]),
            temporal_scope=_temporal(item.get("temporal_scope")), metadata=item.get("metadata", {}),
        )
        for item in data["observations"]
    )
    events = tuple(
        EventRecord(
            id=item["id"], description=item["description"], lineage=_lineage(item["lineage"]),
            temporal_scope=_temporal(item.get("temporal_scope")), metadata=item.get("metadata", {}),
        )
        for item in data["events"]
    )
    evidence = tuple(
        EvidenceRecord(
            id=item["id"], content=item["content"], stance=EvidenceStance(item["stance"]),
            lineage=_lineage(item["lineage"]), temporal_scope=_temporal(item.get("temporal_scope")),
            metadata=item.get("metadata", {}),
        )
        for item in data["evidence"]
    )
    claims = tuple(
        CharacterClaim(
            id=item["id"], statement=item["statement"], status=ArtifactStatus(item["status"]),
            lineage=_lineage(item["lineage"]),
            transitions=tuple(
                StatusTransition(
                    from_status=ArtifactStatus(transition["from_status"]),
                    to_status=ArtifactStatus(transition["to_status"]),
                    reason=transition["reason"], timestamp=datetime.fromisoformat(transition["timestamp"]),
                )
                for transition in item.get("transitions", ())
            ),
            temporal_scope=_temporal(item.get("temporal_scope")), metadata=item.get("metadata", {}),
        )
        for item in data["claims"]
    )
    snapshots = tuple(
        CharacterStateSnapshot(
            id=item["id"], version=item["version"], lineage=_lineage(item["lineage"]),
            temporal_scope=_temporal(item.get("temporal_scope")),
            previous_snapshot_id=item.get("previous_snapshot_id"), metadata=item.get("metadata", {}),
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in data["snapshots"]
    )
    return ReconstructionBundle(
        id=data["id"], version=data["version"], sources=sources, source_units=units,
        observations=observations, events=events, evidence=evidence, claims=claims,
        snapshots=snapshots, previous_version=data.get("previous_version"), metadata=data.get("metadata", {}),
    )
