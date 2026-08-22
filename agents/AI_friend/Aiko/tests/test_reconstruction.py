from dataclasses import replace

import pytest

from ai_friend.reconstruction.interfaces import ReconstructionRepository
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
from ai_friend.reconstruction.pipeline import ReconstructionPipeline
from ai_friend.reconstruction.provenance import Lineage, trace_claim_sources
from ai_friend.reconstruction.repository import InMemoryReconstructionRepository
from ai_friend.reconstruction.validation import ReconstructionValidationError, validate_bundle


def synthetic_bundle() -> ReconstructionBundle:
    source = SourceReference("source-1", "Synthetic scene", "fixture://scene/1", "text/plain")
    unit = SourceUnit("unit-1", source.id, "The subject returns the lost item.", "paragraph:1")
    observation = ObservationRecord(
        "observation-1",
        "The subject returned an item they could have kept.",
        Lineage(source_unit_ids=(unit.id,)),
    )
    event = EventRecord(
        "event-1",
        "A lost item was returned.",
        Lineage(parent_artifact_ids=(observation.id,)),
        TemporalScope(label="synthetic-period-a"),
    )
    evidence = EvidenceRecord(
        "evidence-1",
        "The observed choice supports a provisional honesty hypothesis.",
        EvidenceStance.SUPPORTS,
        Lineage(parent_artifact_ids=(event.id,)),
        TemporalScope(label="synthetic-period-a"),
    )
    claim = CharacterClaim(
        "claim-1",
        "The subject may value honesty.",
        ArtifactStatus.CONSOLIDATED,
        Lineage(parent_artifact_ids=(evidence.id,)),
        transitions=(
            StatusTransition(ArtifactStatus.CANDIDATE, ArtifactStatus.SUPPORTED, "synthetic review"),
            StatusTransition(ArtifactStatus.SUPPORTED, ArtifactStatus.CONSOLIDATED, "synthetic consolidation"),
        ),
        temporal_scope=TemporalScope(label="synthetic-period-a"),
    )
    snapshot = CharacterStateSnapshot(
        "snapshot-1",
        1,
        Lineage(parent_artifact_ids=(claim.id,)),
        TemporalScope(label="synthetic-period-a"),
    )
    return ReconstructionBundle(
        "synthetic-character",
        1,
        sources=(source,),
        source_units=(unit,),
        observations=(observation,),
        events=(event,),
        evidence=(evidence,),
        claims=(claim,),
        snapshots=(snapshot,),
    )


def test_claim_traces_through_evidence_to_source() -> None:
    bundle = synthetic_bundle()

    assert validate_bundle(bundle).is_valid
    assert trace_claim_sources(bundle, "claim-1") == bundle.sources
    assert isinstance(bundle.evidence[0], EvidenceRecord)
    assert isinstance(bundle.claims[0], CharacterClaim)
    assert type(bundle.evidence[0]) is not type(bundle.claims[0])


def test_candidate_and_unresolved_claims_are_not_consolidated() -> None:
    base = synthetic_bundle()
    candidate = replace(base.claims[0], status=ArtifactStatus.CANDIDATE, transitions=())
    unresolved = replace(base.claims[0], id="claim-2", status=ArtifactStatus.UNRESOLVED, transitions=())
    bundle = replace(base, claims=(candidate, unresolved), snapshots=())

    assert validate_bundle(bundle).is_valid
    assert all(claim.status is not ArtifactStatus.CONSOLIDATED for claim in bundle.claims)


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (
            lambda bundle: replace(
                bundle,
                evidence=(replace(bundle.evidence[0], lineage=Lineage()),),
            ),
            "missing_source_lineage",
        ),
        (
            lambda bundle: replace(
                bundle,
                evidence=(replace(bundle.evidence[0], lineage=Lineage(parent_artifact_ids=("evidence-1",))),),
            ),
            "self_reference",
        ),
        (
            lambda bundle: replace(
                bundle,
                claims=(replace(bundle.claims[0], lineage=Lineage(parent_artifact_ids=("missing",))),),
                snapshots=(),
            ),
            "missing_reference",
        ),
        (
            lambda bundle: replace(
                bundle,
                claims=(replace(bundle.claims[0], transitions=()),),
            ),
            "implicit_promotion",
        ),
        (
            lambda bundle: replace(
                bundle,
                evidence=(
                    replace(
                        bundle.evidence[0],
                        lineage=Lineage(
                            source_unit_ids=("unit-1",),
                            parent_artifact_ids=("claim-1",),
                        ),
                    ),
                ),
                snapshots=(),
            ),
            "derived_state_as_evidence",
        ),
    ],
)
def test_integrity_errors_are_surfaced(mutate, expected_code: str) -> None:
    report = validate_bundle(mutate(synthetic_bundle()))

    assert not report.is_valid
    assert expected_code in {issue.code for issue in report.issues}


def test_repository_preserves_versions_and_is_replaceable() -> None:
    class AlternativeRepository(ReconstructionRepository):
        def __init__(self) -> None:
            self.saved: list[ReconstructionBundle] = []

        def save(self, bundle: ReconstructionBundle) -> None:
            self.saved.append(bundle)

        def get(self, bundle_id: str, version: int | None = None) -> ReconstructionBundle | None:
            matches = [item for item in self.saved if item.id == bundle_id]
            if version is not None:
                return next((item for item in matches if item.version == version), None)
            return matches[-1] if matches else None

        def versions(self, bundle_id: str) -> tuple[int, ...]:
            return tuple(item.version for item in self.saved if item.id == bundle_id)

    first = synthetic_bundle()
    second = replace(first, version=2, previous_version=1, snapshots=first.snapshots + (
        replace(first.snapshots[0], id="snapshot-2", version=2, previous_snapshot_id="snapshot-1"),
    ))

    memory_repository = InMemoryReconstructionRepository()
    memory_pipeline = ReconstructionPipeline(memory_repository)
    memory_pipeline.save(first)
    memory_pipeline.save(second)
    assert memory_repository.versions(first.id) == (1, 2)
    assert memory_pipeline.load(first.id) == second

    alternative = AlternativeRepository()
    alternative_pipeline = ReconstructionPipeline(alternative)
    alternative_pipeline.save(first)
    assert alternative_pipeline.load(first.id) == first


def test_pipeline_rejects_invalid_bundle() -> None:
    invalid = replace(
        synthetic_bundle(),
        claims=(replace(synthetic_bundle().claims[0], transitions=()),),
    )

    with pytest.raises(ReconstructionValidationError):
        ReconstructionPipeline(InMemoryReconstructionRepository()).save(invalid)
