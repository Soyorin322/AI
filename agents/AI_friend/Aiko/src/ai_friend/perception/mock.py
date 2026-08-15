from collections import deque
from collections.abc import Iterable

from ai_friend.perception.interfaces import PerceptionSource
from ai_friend.perception.models import PerceptionEvent


class MockPerceptionSource(PerceptionSource):
    def __init__(self, events: Iterable[PerceptionEvent] = ()) -> None:
        self._events = deque(events)

    def next_event(self) -> PerceptionEvent | None:
        return self._events.popleft() if self._events else None

