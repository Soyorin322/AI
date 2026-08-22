from abc import ABC, abstractmethod

from ai_friend.memory.models import MemoryFormationDecision, MemoryRecord


class MemoryFormationPolicy(ABC):
    """Replaceable decision boundary; no retention algorithm is mandated."""

    @abstractmethod
    def decide(self, event_id: str) -> MemoryFormationDecision: ...


class MemoryStore(ABC):
    """Stores experience-derived records independently of Knowledge."""

    @abstractmethod
    def add(self, record: MemoryRecord) -> None: ...

    @abstractmethod
    def get(self, record_id: str) -> MemoryRecord | None: ...

    @abstractmethod
    def search(self, query: str) -> list[MemoryRecord]: ...
