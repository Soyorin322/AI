from ai_friend.character.interfaces import CharacterProvider
from ai_friend.character.models import CharacterProfile


class MockCharacterProvider(CharacterProvider):
    def __init__(self, profile: CharacterProfile) -> None:
        self._profile = profile

    def profile(self) -> CharacterProfile:
        return self._profile

