from abc import ABC, abstractmethod

from ai_friend.perception.models import PerceptionEvent


class PerceptionSource(ABC):
    """Produces typed observations without changing other subsystems."""

    @abstractmethod
    def next_event(self) -> PerceptionEvent | None: ...

