from abc import ABC, abstractmethod

from ai_friend.character.models import CharacterProfile


class CharacterProvider(ABC):
    """Supplies the current character profile without exposing its storage."""

    @abstractmethod
    def profile(self) -> CharacterProfile: ...

