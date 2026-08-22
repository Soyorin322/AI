from ai_friend.reconstruction.interfaces import ReconstructionRepository
from ai_friend.reconstruction.models import ReconstructionBundle
from ai_friend.reconstruction.validation import ValidationReport, validate_bundle


class ReconstructionPipeline:
    """Minimal reconstruction orchestration boundary.

    It validates and persists caller-produced artifacts. Extraction, appraisal,
    consolidation decisions, and LLM use are intentionally outside Task 003.
    """

    def __init__(self, repository: ReconstructionRepository) -> None:
        self._repository = repository

    def validate(self, bundle: ReconstructionBundle) -> ValidationReport:
        return validate_bundle(bundle)

    def save(self, bundle: ReconstructionBundle) -> None:
        report = self.validate(bundle)
        report.raise_for_errors()
        self._repository.save(bundle)

    def load(self, bundle_id: str, version: int | None = None) -> ReconstructionBundle | None:
        return self._repository.get(bundle_id, version)

