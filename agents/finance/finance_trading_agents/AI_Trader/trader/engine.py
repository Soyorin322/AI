"""
Per-wake engine helper for the Claude session.

  python trader/engine.py poll     -> touch heartbeat; print {loop_on, due, ...}
  python trader/engine.py record   -> mark a trading cycle as just completed

The Claude session calls `poll` every wake. If due+on it runs a full trading
cycle (snapshot -> decide -> execute -> report) then calls `record`. Otherwise
the heartbeat alone keeps the control page showing the engine as online.
"""

import json
import sys
from datetime import datetime, timezone

import config
import state

# Don't trade more often than ~80% of the mode's cadence even if woken sooner.
DUE_AFTER_MINUTES = max(1, round(config.INTERVAL_MINUTES * 0.8))


def _minutes_since(iso: str | None) -> float:
    if not iso:
        return 1e9
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return 1e9
    return (datetime.now(timezone.utc) - dt).total_seconds() / 60


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "poll"
    if cmd == "record":
        s = state.record_cycle()
        print(json.dumps({"recorded": True, "cycle_count": s["cycle_count"]}))
        return
    s = state.touch_heartbeat()
    mins = _minutes_since(s.get("last_cycle_at"))
    print(json.dumps({
        "loop_on": s.get("loop_on", False),
        "minutes_since_cycle": round(mins, 1),
        "due": bool(s.get("loop_on", False)) and mins >= DUE_AFTER_MINUTES,
        "interval_minutes": config.INTERVAL_MINUTES,
        "mode": config.MODE,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
