from abc import ABC, abstractmethod
from typing import Protocol

from ai_friend.skills.models import SkillMetadata


class SkillRegistry(ABC):
    """Lists independently loadable skill resources."""

    @abstractmethod
    def discover(self) -> list[SkillMetadata]: ...


class CapabilitySkill(Protocol):
    """Technical execution boundary, separate from character skill evidence."""

    @property
    def skill_id(self) -> str: ...

    def capability_ids(self) -> tuple[str, ...]: ...
