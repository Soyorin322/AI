from ai_friend.reconstruction.interfaces import ReconstructionRepository
from ai_friend.reconstruction.models import ReconstructionBundle


class InMemoryReconstructionRepository(ReconstructionRepository):
    """Simple revision-preserving implementation for bootstrap and tests."""

    def __init__(self) -> None:
        self._bundles: dict[tuple[str, int], ReconstructionBundle] = {}

    def save(self, bundle: ReconstructionBundle) -> None:
        key = (bundle.id, bundle.version)
        if key in self._bundles:
            raise ValueError(f"bundle revision already exists: {bundle.id} v{bundle.version}")
        self._bundles[key] = bundle

    def get(self, bundle_id: str, version: int | None = None) -> ReconstructionBundle | None:
        if version is not None:
            return self._bundles.get((bundle_id, version))
        known = self.versions(bundle_id)
        return self._bundles.get((bundle_id, known[-1])) if known else None

    def versions(self, bundle_id: str) -> tuple[int, ...]:
        return tuple(sorted(version for stored_id, version in self._bundles if stored_id == bundle_id))

