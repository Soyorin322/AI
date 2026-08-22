from abc import ABC, abstractmethod

from ai_friend.reconstruction.models import ReconstructionBundle


class ReconstructionRepository(ABC):
    """Persistence boundary for Aiko-owned reconstruction bundles."""

    @abstractmethod
    def save(self, bundle: ReconstructionBundle) -> None: ...

    @abstractmethod
    def get(self, bundle_id: str, version: int | None = None) -> ReconstructionBundle | None: ...

    @abstractmethod
    def versions(self, bundle_id: str) -> tuple[int, ...]: ...

