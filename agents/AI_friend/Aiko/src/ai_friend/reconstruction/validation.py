from dataclasses import dataclass

from ai_friend.reconstruction.models import (
    ArtifactStatus,
    CharacterClaim,
    CharacterStateSnapshot,
    EvidenceRecord,
    ReconstructionBundle,
    SourceUnitGrounding,
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    artifact_id: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def raise_for_errors(self) -> None:
        if self.issues:
            raise ReconstructionValidationError(self)


class ReconstructionValidationError(ValueError):
    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__("; ".join(issue.message for issue in report.issues))


def validate_bundle(bundle: ReconstructionBundle) -> ValidationReport:
    """Detect structural lineage and maturity errors without judging psychology."""

    issues: list[ValidationIssue] = []
    sources = {source.id: source for source in bundle.sources}
    units = {unit.id: unit for unit in bundle.source_units}
    collections = (bundle.observations, bundle.events, bundle.evidence, bundle.claims, bundle.snapshots)
    derived_items = [artifact for collection in collections for artifact in collection]

    all_ids = [*sources, *units, *(artifact.id for artifact in derived_items)]
    for source in bundle.sources:
        if not source.approved:
            issues.append(
                ValidationIssue(
                    "unapproved_source",
                    f"source {source.id} is not explicitly approved",
                    source.id,
                )
            )
        if source.metadata.get("source_role") == "reference_note":
            issues.append(
                ValidationIssue(
                    "reference_note_as_source",
                    f"source {source.id} is a navigation note, not canonical evidence",
                    source.id,
                )
            )
    for artifact_id in sorted({item for item in all_ids if all_ids.count(item) > 1}):
        issues.append(ValidationIssue("duplicate_id", f"duplicate artifact id: {artifact_id}", artifact_id))

    for unit in bundle.source_units:
        if unit.source_id not in sources:
            issues.append(
                ValidationIssue("missing_source", f"source unit {unit.id} references missing source {unit.source_id}", unit.id)
            )
        if unit.grounding is None:
            issues.append(
                ValidationIssue(
                    "unmarked_source_unit",
                    f"source unit {unit.id} must declare exact-text or immutable-reference grounding",
                    unit.id,
                )
            )
        elif not unit.locator or not unit.integrity_hash:
            issues.append(
                ValidationIssue(
                    "incomplete_source_grounding",
                    f"source unit {unit.id} requires an exact locator and integrity hash",
                    unit.id,
                )
            )
        elif unit.grounding is SourceUnitGrounding.EXACT_TEXT and not unit.content:
            issues.append(ValidationIssue("missing_exact_text", f"source unit {unit.id} has no exact text", unit.id))
        elif unit.grounding is SourceUnitGrounding.IMMUTABLE_EXACT_SPAN_REFERENCE and unit.content:
            issues.append(
                ValidationIssue(
                    "reference_contains_derived_content",
                    f"immutable source unit reference {unit.id} must not contain derived prose",
                    unit.id,
                )
            )

    derived = {artifact.id: artifact for artifact in derived_items}
    known_ids = set(sources) | set(units) | set(derived)
    for artifact in derived_items:
        lineage = artifact.lineage
        if artifact.id in lineage.parent_artifact_ids:
            issues.append(ValidationIssue("self_reference", f"artifact {artifact.id} references itself", artifact.id))
        for reference_id in (*lineage.source_ids, *lineage.source_unit_ids, *lineage.parent_artifact_ids):
            if reference_id not in known_ids:
                issues.append(
                    ValidationIssue(
                        "missing_reference",
                        f"artifact {artifact.id} references missing id {reference_id}",
                        artifact.id,
                    )
                )
        for source_id in lineage.source_ids:
            if source_id not in sources and source_id in known_ids:
                issues.append(ValidationIssue("invalid_source_reference", f"{source_id} is not a source", artifact.id))
        for unit_id in lineage.source_unit_ids:
            if unit_id not in units and unit_id in known_ids:
                issues.append(ValidationIssue("invalid_unit_reference", f"{unit_id} is not a source unit", artifact.id))

    _validate_parent_cycles(derived, issues)
    _validate_stage_links(bundle, derived, issues)
    _validate_claim_status(bundle.claims, issues)
    _validate_source_lineage(bundle.evidence, sources, units, derived, issues)
    _validate_snapshots(bundle, derived, issues)
    return ValidationReport(tuple(issues))


def _validate_parent_cycles(derived: dict[str, object], issues: list[ValidationIssue]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str) -> None:
        if artifact_id in visiting:
            issues.append(ValidationIssue("lineage_cycle", f"lineage cycle includes {artifact_id}", artifact_id))
            return
        if artifact_id in visited or artifact_id not in derived:
            return
        visiting.add(artifact_id)
        artifact = derived[artifact_id]
        for parent_id in artifact.lineage.parent_artifact_ids:  # type: ignore[attr-defined]
            visit(parent_id)
        visiting.remove(artifact_id)
        visited.add(artifact_id)

    for artifact_id in derived:
        visit(artifact_id)


def _validate_stage_links(
    bundle: ReconstructionBundle,
    derived: dict[str, object],
    issues: list[ValidationIssue],
) -> None:
    for record in bundle.evidence:
        parents = [derived[parent_id] for parent_id in record.lineage.parent_artifact_ids if parent_id in derived]
        if any(isinstance(parent, (CharacterClaim, CharacterStateSnapshot)) for parent in parents):
            issues.append(
                ValidationIssue(
                    "derived_state_as_evidence",
                    f"evidence {record.id} uses a claim or snapshot as evidence",
                    record.id,
                )
            )

    for claim in bundle.claims:
        parents = [derived[parent_id] for parent_id in claim.lineage.parent_artifact_ids if parent_id in derived]
        if not any(isinstance(parent, EvidenceRecord) for parent in parents):
            issues.append(
                ValidationIssue("claim_without_evidence", f"claim {claim.id} has no evidence parent", claim.id)
            )
        if any(isinstance(parent, CharacterClaim) for parent in parents):
            issues.append(
                ValidationIssue("claim_as_evidence", f"claim {claim.id} uses another claim as evidence", claim.id)
            )


def _validate_claim_status(claims: tuple[CharacterClaim, ...], issues: list[ValidationIssue]) -> None:
    for claim in claims:
        if claim.transitions:
            current = claim.transitions[0].from_status
            for transition in claim.transitions:
                if transition.from_status != current:
                    issues.append(
                        ValidationIssue("broken_status_history", f"claim {claim.id} has discontinuous status history", claim.id)
                    )
                    break
                current = transition.to_status
            if current != claim.status:
                issues.append(
                    ValidationIssue("status_mismatch", f"claim {claim.id} status does not match its history", claim.id)
                )
        elif claim.status is not ArtifactStatus.CANDIDATE and claim.status is not ArtifactStatus.UNRESOLVED:
            issues.append(
                ValidationIssue("implicit_promotion", f"claim {claim.id} has no explicit status transition", claim.id)
            )
        if claim.status is ArtifactStatus.CONSOLIDATED:
            if not claim.transitions or claim.transitions[-1].from_status is not ArtifactStatus.SUPPORTED:
                issues.append(
                    ValidationIssue(
                        "unsafe_consolidation",
                        f"claim {claim.id} was not explicitly promoted from supported to consolidated",
                        claim.id,
                    )
                )


def _validate_source_lineage(
    evidence: tuple[EvidenceRecord, ...],
    sources: dict[str, object],
    units: dict[str, object],
    derived: dict[str, object],
    issues: list[ValidationIssue],
) -> None:
    def reaches_source(artifact_id: str, seen: set[str]) -> bool:
        if artifact_id in seen or artifact_id not in derived:
            return False
        seen.add(artifact_id)
        artifact = derived[artifact_id]
        lineage = artifact.lineage  # type: ignore[attr-defined]
        if any(source_id in sources for source_id in lineage.source_ids):
            return True
        if any(unit_id in units for unit_id in lineage.source_unit_ids):
            return True
        return any(reaches_source(parent_id, seen) for parent_id in lineage.parent_artifact_ids)

    for record in evidence:
        if not reaches_source(record.id, set()):
            issues.append(
                ValidationIssue("missing_source_lineage", f"evidence {record.id} cannot be traced to a source", record.id)
            )


def _validate_snapshots(
    bundle: ReconstructionBundle,
    derived: dict[str, object],
    issues: list[ValidationIssue],
) -> None:
    snapshot_ids = {snapshot.id for snapshot in bundle.snapshots}
    for snapshot in bundle.snapshots:
        if snapshot.version < 1:
            issues.append(ValidationIssue("invalid_snapshot_version", "snapshot version must be positive", snapshot.id))
        if snapshot.previous_snapshot_id is not None and snapshot.previous_snapshot_id not in snapshot_ids:
            issues.append(
                ValidationIssue(
                    "missing_previous_snapshot",
                    f"snapshot {snapshot.id} references missing previous snapshot {snapshot.previous_snapshot_id}",
                    snapshot.id,
                )
            )
        claim_parent_count = 0
        for parent_id in snapshot.lineage.parent_artifact_ids:
            parent = derived.get(parent_id)
            if isinstance(parent, CharacterClaim):
                claim_parent_count += 1
                if parent.status is not ArtifactStatus.CONSOLIDATED:
                    issues.append(
                        ValidationIssue(
                            "unconsolidated_snapshot_claim",
                            f"snapshot {snapshot.id} includes non-consolidated claim {parent_id}",
                            snapshot.id,
                        )
                    )
            elif parent is not None:
                issues.append(
                    ValidationIssue(
                        "invalid_snapshot_parent",
                        f"snapshot {snapshot.id} parent {parent_id} is not a character claim",
                        snapshot.id,
                    )
                )
        if claim_parent_count == 0:
            issues.append(
                ValidationIssue("snapshot_without_claims", f"snapshot {snapshot.id} has no claim parents", snapshot.id)
            )
