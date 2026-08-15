from abc import ABC, abstractmethod

from ai_friend.knowledge.models import KnowledgeRecord


class KnowledgeStore(ABC):
    """Retrieves information available to a character."""

    @abstractmethod
    def add(self, record: KnowledgeRecord) -> None: ...

    @abstractmethod
    def get(self, record_id: str) -> KnowledgeRecord | None: ...

    @abstractmethod
    def search(self, query: str) -> list[KnowledgeRecord]: ...

