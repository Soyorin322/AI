from ai_friend.knowledge.interfaces import KnowledgeStore
from ai_friend.knowledge.models import KnowledgeRecord


class InMemoryKnowledgeStore(KnowledgeStore):
    def __init__(self) -> None:
        self._records: dict[str, KnowledgeRecord] = {}

    def add(self, record: KnowledgeRecord) -> None:
        self._records[record.id] = record

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self._records.get(record_id)

    def search(self, query: str) -> list[KnowledgeRecord]:
        needle = query.casefold()
        return [record for record in self._records.values() if needle in record.content.casefold()]

