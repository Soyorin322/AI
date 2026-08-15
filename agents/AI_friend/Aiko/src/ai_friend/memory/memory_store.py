from ai_friend.memory.interfaces import MemoryStore
from ai_friend.memory.models import MemoryRecord


class InMemoryMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def add(self, record: MemoryRecord) -> None:
        self._records[record.id] = record

    def get(self, record_id: str) -> MemoryRecord | None:
        return self._records.get(record_id)

    def search(self, query: str) -> list[MemoryRecord]:
        needle = query.casefold()
        return [record for record in self._records.values() if needle in record.content.casefold()]

