from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

