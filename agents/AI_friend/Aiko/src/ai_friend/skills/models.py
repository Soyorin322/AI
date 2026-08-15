from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SkillMetadata:
    name: str
    description: str
    path: Path

