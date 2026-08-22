"""Validate the committed Reirin v0.1 bundle and print artifact counts."""

from collections import Counter
from pathlib import Path

from ai_friend.reconstruction.provenance import trace_claim_sources
from ai_friend.reconstruction.validation import validate_bundle

from bundle_io import load_bundle


def main() -> None:
    bundle = load_bundle(Path(__file__).with_name("bundle_v0.1.json"))
    report = validate_bundle(bundle)
    report.raise_for_errors()
    allowed_sources = {"reirin-vol1", "reirin-vol2"}
    for claim in bundle.claims:
        if claim.status.value == "consolidated":
            traced = {source.id for source in trace_claim_sources(bundle, claim.id)}
            if not traced or not traced <= allowed_sources:
                raise ValueError(f"invalid source boundary for {claim.id}: {sorted(traced)}")
    statuses = Counter(claim.status.value for claim in bundle.claims)
    print(
        "valid Reirin v0.1: "
        f"sources={len(bundle.sources)} units={len(bundle.source_units)} "
        f"observations={len(bundle.observations)} events={len(bundle.events)} "
        f"evidence={len(bundle.evidence)} claims={len(bundle.claims)} "
        f"snapshots={len(bundle.snapshots)} statuses={dict(sorted(statuses.items()))}"
    )


if __name__ == "__main__":
    main()
