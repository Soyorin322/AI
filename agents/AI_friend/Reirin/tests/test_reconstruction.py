import json
from collections import Counter
from pathlib import Path

from ai_friend.reconstruction.models import ArtifactStatus, CharacterClaim, CharacterStateSnapshot, EvidenceRecord
from ai_friend.reconstruction.provenance import trace_claim_sources
from ai_friend.reconstruction.validation import validate_bundle

from build_bundle import build_bundle
from bundle_io import bundle_to_dict, load_bundle


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = ROOT / "reconstruction" / "bundle_v0.1.json"
MANIFEST_PATH = ROOT / "reconstruction" / "manifest.json"
ALLOWED_SOURCE_IDS = {"reirin-vol1", "reirin-vol2"}
EXCLUDED_MARKER = "第三卷"


def test_committed_bundle_is_deterministic_and_valid() -> None:
    loaded = load_bundle(BUNDLE_PATH)
    built = build_bundle()

    assert loaded == built
    assert bundle_to_dict(loaded) == json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    assert validate_bundle(loaded).is_valid


def test_manifest_freezes_only_volume_one_and_two() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    included = manifest["included_sources"]

    assert [item["volume"] for item in included] == [1, 2]
    assert {item["blob_sha"] for item in included} == {
        "4a6109af0305c9d12c14f81862df15c18bb92c67",
        "8fcfebd854639c8ec4d42b98ff17810d69d907fe",
    }
    assert all(EXCLUDED_MARKER not in item["path"] for item in included)
    assert manifest["excluded_sources"][0]["status"].startswith("hard-excluded")


def test_all_artifact_lineage_is_within_approved_sources() -> None:
    bundle = load_bundle(BUNDLE_PATH)

    assert {source.id for source in bundle.sources} == ALLOWED_SOURCE_IDS
    assert all(unit.source_id in ALLOWED_SOURCE_IDS for unit in bundle.source_units)
    assert all(EXCLUDED_MARKER not in source.locator for source in bundle.sources)
    for claim in bundle.claims:
        if claim.status is ArtifactStatus.CONSOLIDATED:
            traced = {source.id for source in trace_claim_sources(bundle, claim.id)}
            assert traced
            assert traced <= ALLOWED_SOURCE_IDS


def test_identity_and_body_are_distinct_during_swap() -> None:
    bundle = load_bundle(BUNDLE_PATH)
    swapped = [unit for unit in bundle.source_units if unit.metadata["body_identity"] == "朱慧月"]

    assert swapped
    assert all(unit.metadata["character_identity"] == "黃玲琳" for unit in swapped)
    identity_claim = next(claim for claim in bundle.claims if claim.id == "claim-identity")
    assert identity_claim.status is ArtifactStatus.CONSOLIDATED


def test_claims_and_snapshots_preserve_integrity_and_uncertainty() -> None:
    bundle = load_bundle(BUNDLE_PATH)
    derived = {
        artifact.id: artifact
        for collection in (bundle.observations, bundle.events, bundle.evidence, bundle.claims, bundle.snapshots)
        for artifact in collection
    }
    statuses = Counter(claim.status for claim in bundle.claims)

    assert statuses[ArtifactStatus.CANDIDATE] > 0
    assert statuses[ArtifactStatus.UNRESOLVED] > 0
    for record in bundle.evidence:
        assert all(not isinstance(derived.get(parent_id), (CharacterClaim, CharacterStateSnapshot)) for parent_id in record.lineage.parent_artifact_ids)
    for snapshot in bundle.snapshots:
        assert snapshot.metadata["knowledge_boundary"] == "Volume 1 and Volume 2 only"
        assert all(
            isinstance(derived[parent_id], CharacterClaim)
            and derived[parent_id].status is ArtifactStatus.CONSOLIDATED
            for parent_id in snapshot.lineage.parent_artifact_ids
        )
    assert all(type(record) is EvidenceRecord for record in bundle.evidence)


def test_aiko_has_no_reirin_dependency() -> None:
    aiko_root = ROOT.parent / "Aiko"
    for path in (aiko_root / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8").casefold()
        assert "reirin" not in text
        assert "character_data/reirin" not in text
