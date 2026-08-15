#!/usr/bin/env python
"""
auto-buy-alert · intraday "hottest US stocks" list (deterministic stage 1 for the
'hot' session).

Composite hotness = dollar-volume activity (Yahoo most-actives) + absolute daily
move (Yahoo day gainers/losers). Pulls the lists via yfinance's predefined
screeners, merges them, ranks, and prints the top-N as JSON for the orchestrator
(Claude) to add "why hot / news" analysis and post a digest.

Usage: python hot_list.py [--top 10]
"""
import argparse
import json
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

warnings.filterwarnings("ignore")

import yfinance as yf

ET = ZoneInfo("America/New_York")
SCREENS = ["most_actives", "day_gainers", "day_losers"]
MIN_PRICE = 1.0  # skip sub-$1 penny names


def fetch_screen(key, count=50):
    try:
        r = yf.screen(key, count=count)
        return r.get("quotes", []) if isinstance(r, dict) else []
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    union = {}
    source_counts = {}
    for key in SCREENS:
        quotes = fetch_screen(key)
        source_counts[key] = len(quotes)
        for q in quotes:
            sym = q.get("symbol")
            price = q.get("regularMarketPrice") or 0
            if not sym or price < MIN_PRICE:
                continue
            e = union.setdefault(sym, {
                "symbol": sym,
                "name": q.get("shortName") or q.get("longName") or sym,
                "price": round(float(price), 4),
                "chg_pct": round(float(q.get("regularMarketChangePercent") or 0.0), 2),
                "volume": int(q.get("regularMarketVolume") or 0),
                "market_cap": q.get("marketCap"),
                "in_lists": set(),
            })
            e["in_lists"].add(key)

    if not union:
        print(json.dumps({"session": "hot", "error": "no screener data",
                          "source_counts": source_counts}))
        return

    for e in union.values():
        e["dollar_volume"] = round(e["price"] * e["volume"], 2)

    # dollar-volume activity score (0..50) by rank
    by_dv = sorted(union.values(), key=lambda x: x["dollar_volume"], reverse=True)
    n = len(by_dv)
    for idx, e in enumerate(by_dv):
        e["_dv_score"] = round(50.0 * (1.0 - idx / max(n - 1, 1)), 1)

    for e in union.values():
        move_score = min(abs(e["chg_pct"]), 25.0) * 2.0          # 0..50
        multi_bonus = (len(e["in_lists"]) - 1) * 5.0             # cross-list bonus
        e["hotness"] = round(e["_dv_score"] + move_score + multi_bonus, 1)

    ranked = sorted(union.values(), key=lambda x: x["hotness"], reverse=True)[:args.top]

    top = []
    for e in ranked:
        top.append({
            "symbol": e["symbol"],
            "name": e["name"],
            "price": e["price"],
            "chg_pct": e["chg_pct"],
            "volume": e["volume"],
            "dollar_volume": e["dollar_volume"],
            "market_cap": e["market_cap"],
            "in_lists": sorted(e["in_lists"]),
            "hotness": e["hotness"],
        })

    report = {
        "session": "hot",
        "generated_at": datetime.now(ET).isoformat(timespec="seconds"),
        "top_n": args.top,
        "source_counts": source_counts,
        "top": top,
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
