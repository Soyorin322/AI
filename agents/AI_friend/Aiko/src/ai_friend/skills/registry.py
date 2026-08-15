from pathlib import Path

from ai_friend.skills.interfaces import SkillRegistry
from ai_friend.skills.models import SkillMetadata


class DirectorySkillRegistry(SkillRegistry):
    def __init__(self, root: Path) -> None:
        self._root = root

    def discover(self) -> list[SkillMetadata]:
        skills: list[SkillMetadata] = []
        if not self._root.exists():
            return skills
        for skill_file in sorted(self._root.glob("*/SKILL.md")):
            lines = skill_file.read_text(encoding="utf-8").splitlines()
            name = next((line[2:].strip() for line in lines if line.startswith("# ")), skill_file.parent.name)
            description = next((line.strip() for line in lines if line.strip() and not line.startswith("#")), "")
            skills.append(SkillMetadata(name=name, description=description, path=skill_file.parent))
        return skills

