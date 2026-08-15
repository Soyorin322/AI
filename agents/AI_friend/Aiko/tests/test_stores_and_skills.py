from pathlib import Path

from ai_friend.knowledge.memory_store import InMemoryKnowledgeStore
from ai_friend.knowledge.models import KnowledgeRecord
from ai_friend.memory.memory_store import InMemoryMemoryStore
from ai_friend.memory.models import MemoryRecord
from ai_friend.skills.registry import DirectorySkillRegistry


def test_knowledge_store_round_trip() -> None:
    store = InMemoryKnowledgeStore()
    record = KnowledgeRecord("k1", "The sky is blue")
    store.add(record)
    assert store.get("k1") == record
    assert store.search("SKY") == [record]


def test_memory_store_round_trip() -> None:
    store = InMemoryMemoryStore()
    record = MemoryRecord("m1", "We discussed architecture")
    store.add(record)
    assert store.get("m1") == record
    assert store.search("architecture") == [record]


def test_skill_discovery_finds_example() -> None:
    root = Path(__file__).resolve().parents[1] / "skills"
    skills = DirectorySkillRegistry(root).discover()
    assert [skill.name for skill in skills] == ["Example Skill"]
    assert skills[0].path.name == "example_skill"
