"""
Local trade journal (append-only JSONL) + per-local-day trade counter.
Gives the /loop memory across cycles and enforces the daily trade limit.
"""

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import config

_TZ = ZoneInfo(config.LOCAL_TZ)


def _today() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d")


def record(entry: dict) -> None:
    entry = dict(entry)
    entry.setdefault("ts_utc", datetime.now(ZoneInfo("UTC")).isoformat())
    entry.setdefault("local_day", _today())
    with open(config.JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _jpath(mode=None) -> str:
    if mode is None:
        return config.JOURNAL_PATH
    return os.path.join(config.HERE, config.MODES[mode]["journal_file"])


def _read_all(mode=None) -> list[dict]:
    path = _jpath(mode)
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def trades_today() -> int:
    day = _today()
    return sum(1 for e in _read_all()
               if e.get("local_day") == day and e.get("event") == "trade")


def recent(n: int = 10, mode=None) -> list[dict]:
    return _read_all(mode)[-n:]
