from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

