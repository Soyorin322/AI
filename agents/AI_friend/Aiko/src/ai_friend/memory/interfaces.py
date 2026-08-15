from abc import ABC, abstractmethod

from ai_friend.memory.models import MemoryRecord


class MemoryStore(ABC):
    """Stores experience-derived records independently of Knowledge."""

    @abstractmethod
    def add(self, record: MemoryRecord) -> None: ...

    @abstractmethod
    def get(self, record_id: str) -> MemoryRecord | None: ...

    @abstractmethod
    def search(self, query: str) -> list[MemoryRecord]: ...

