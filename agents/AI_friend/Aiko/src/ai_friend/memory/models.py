from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from ai_friend.core.models import utc_now


class MemoryType(StrEnum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    RELATIONSHIP = "relationship"


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    id: str
    content: str
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: MemoryType = MemoryType.EPISODIC

