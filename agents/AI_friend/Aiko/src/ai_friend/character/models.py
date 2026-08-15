from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CharacterIdentity:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class CharacterState:
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CharacterProfile:
    identity: CharacterIdentity
    description: str
    state: CharacterState

