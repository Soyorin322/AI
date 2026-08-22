"""Portable deterministic JSON serialization for Aiko-owned dataclasses."""

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


def _portable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return _portable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _portable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_portable(item) for item in value]
    return value


def to_portable_json(artifact: Any, *, schema_version: str, artifact_version: str) -> str:
    """Serialize an Aiko contract with explicit portable version metadata."""

    envelope = {
        "artifact": _portable(artifact),
        "artifact_version": artifact_version,
        "schema_version": schema_version,
    }
    return json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
