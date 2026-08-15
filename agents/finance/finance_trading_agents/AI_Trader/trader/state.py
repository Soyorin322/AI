"""
Shared on/off + heartbeat state between the control page and the Claude engine.

Each mode (swing|day) has its own state file. Engine scripts call these with no
`mode` (they use the TRADER_MODE-selected config.STATE_PATH); the control server
passes mode="swing"/"day" to read/write each book independently.
"""

import json
import os
from datetime import datetime, timezone

import config

_DEFAULT = {
    "loop_on": False,
    "engine_heartbeat": None,
    "last_cycle_at": None,
    "cycle_count": 0,
    "interval_minutes": 30,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _path(mode=None) -> str:
    if mode is None:
        return config.STATE_PATH
    return os.path.join(config.HERE, config.MODES[mode]["state_file"])


def load(mode=None) -> dict:
    path = _path(mode)
    if not os.path.exists(path):
        return dict(_DEFAULT)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT)
    return {**_DEFAULT, **data}


def save(data: dict, mode=None) -> None:
    with open(_path(mode), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def set_loop(on: bool, mode=None) -> dict:
    d = load(mode)
    d["loop_on"] = bool(on)
    save(d, mode)
    return d


def touch_heartbeat(mode=None) -> dict:
    d = load(mode)
    d["engine_heartbeat"] = _now()
    save(d, mode)
    return d


def record_cycle(mode=None) -> dict:
    d = load(mode)
    d["engine_heartbeat"] = _now()
    d["last_cycle_at"] = _now()
    d["cycle_count"] = int(d.get("cycle_count", 0)) + 1
    save(d, mode)
    return d
