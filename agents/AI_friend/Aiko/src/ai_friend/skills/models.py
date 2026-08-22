from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SkillMetadata:
    name: str
    description: str
    path: Path


@dataclass(frozen=True, slots=True)
class RuntimeCapability:
    """Executable availability; never canonical character proficiency."""

    skill_id: str
    capability_id: str
    enabled: bool
    implementation: str | None = None
    metadata: dict[str, str] | None = None
