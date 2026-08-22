from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Lineage:
    """Generic source and parent links for a derived artifact."""

    source_ids: tuple[str, ...] = ()
    source_unit_ids: tuple[str, ...] = ()
    parent_artifact_ids: tuple[str, ...] = ()


def trace_claim_sources(bundle: "ReconstructionBundle", claim_id: str) -> tuple["SourceReference", ...]:
    """Trace a claim through parents and source units to source references."""

    from ai_friend.reconstruction.models import ReconstructionBundle, SourceReference

    if not isinstance(bundle, ReconstructionBundle):
        raise TypeError("bundle must be a ReconstructionBundle")

    sources = {source.id: source for source in bundle.sources}
    units = {unit.id: unit for unit in bundle.source_units}
    derived = {
        artifact.id: artifact
        for collection in (bundle.observations, bundle.events, bundle.evidence, bundle.claims, bundle.snapshots)
        for artifact in collection
    }
    if claim_id not in {claim.id for claim in bundle.claims}:
        raise KeyError(claim_id)

    found: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str) -> None:
        if artifact_id in visited:
            return
        visited.add(artifact_id)
        artifact = derived[artifact_id]
        found.update(artifact.lineage.source_ids)
        for unit_id in artifact.lineage.source_unit_ids:
            found.add(units[unit_id].source_id)
        for parent_id in artifact.lineage.parent_artifact_ids:
            visit(parent_id)

    visit(claim_id)
    return tuple(sources[source_id] for source_id in sorted(found))


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_friend.reconstruction.models import ReconstructionBundle, SourceReference

