from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ai_friend.core.models import utc_now


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """Minimal Aiko-owned experience record.

    Memory taxonomy is intentionally deferred. Implementations may use metadata
    for provisional classification without making a research candidate part of
    the framework contract.
    """

    id: str
    content: str
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)
