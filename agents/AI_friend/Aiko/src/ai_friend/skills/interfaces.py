from abc import ABC, abstractmethod

from ai_friend.skills.models import SkillMetadata


class SkillRegistry(ABC):
    """Lists independently loadable skill resources."""

    @abstractmethod
    def discover(self) -> list[SkillMetadata]: ...

