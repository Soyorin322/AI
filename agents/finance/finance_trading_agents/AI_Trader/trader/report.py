"""
Push a real-time P&L summary card to Discord and print it.
Run each cycle (or on demand):  python trader/report.py
"""

import json
import sys

import api
import config
import notify
import portfolio


def main() -> int:
    pos_data = api.get_positions()
    positions = portfolio.enrich_live(pos_data.get("positions", []))
    cash = float(pos_data.get("cash", config.INITIAL_CAPITAL))
    eq = portfolio.snapshot_equity(positions, cash)

    notify.notify_pnl(eq["equity"], cash, eq["total_pnl"], eq["total_pnl_pct"], positions)

    print(json.dumps({
        "equity": round(eq["equity"], 2),
        "cash": round(cash, 2),
        "total_pnl": round(eq["total_pnl"], 2),
        "total_pnl_pct": round(eq["total_pnl_pct"], 3),
        "positions": len(positions),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
