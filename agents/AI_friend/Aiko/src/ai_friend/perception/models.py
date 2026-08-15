from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from ai_friend.core.models import utc_now


@dataclass(frozen=True, slots=True)
class PerceptionEvent:
    modality: str
    source: str
    payload: Any
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=utc_now)

