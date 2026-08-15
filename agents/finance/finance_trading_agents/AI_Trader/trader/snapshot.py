"""
Print a market + account snapshot as JSON. This is what Claude reads each cycle
to make trading decisions. Run:  python trader/snapshot.py
"""

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

import api
import config
import journal
import portfolio

_ET = ZoneInfo("America/New_York")


def is_us_market_open() -> bool:
    now = datetime.now(_ET)
    if now.weekday() >= 5:  # Sat/Sun
        return False
    minutes = now.hour * 60 + now.minute
    return 9 * 60 + 30 <= minutes < 16 * 60  # 09:30–16:00 ET (holidays ignored)


def _market_intel() -> dict:
    out = {"news": [], "macro": []}
    try:
        r = requests.get(f"{config.API_BASE}/api/market-intel/news",
                         params={"limit": 6}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            cats = data.get("categories", []) if isinstance(data, dict) else []
            for c in cats:
                for item in (c.get("items") or [])[:3]:
                    out["news"].append({
                        "category": c.get("category"),
                        "title": item.get("title") or item.get("headline"),
                    })
    except requests.RequestException:
        pass
    return out


def build() -> dict:
    pos_data = api.get_positions()
    positions = portfolio.enrich_live(pos_data.get("positions", []))
    cash = float(pos_data.get("cash", config.INITIAL_CAPITAL))
    eq = portfolio.snapshot_equity(positions, cash)

    us_open = is_us_market_open()
    quotes = {}
    hot_movers: list[dict] = []
    held_price = {(p.get("symbol") or "").upper(): float(p["current_price"])
                  for p in positions if p.get("current_price")}

    if config.MODE == "day":
        # Day book "追热点": quotes are driven by the live yfinance movers board.
        # refresh() here also rewrites day_universe.json so execute.py (a separate
        # process) sees the same names when it checks the universe whitelist.
        if us_open:
            try:
                import hotscan
                hot_movers = hotscan.refresh().get("board", [])
            except Exception:
                hot_movers = []
            for r in hot_movers:
                quotes[f"us-stock:{r['ticker']}"] = r.get("price")
        for sym, pr in held_price.items():  # always keep held names quoted (for exits)
            quotes.setdefault(f"us-stock:{sym}", pr)
    else:
        for market, symbols in config.UNIVERSE.items():
            if market == "us-stock" and not us_open:
                continue  # don't waste rate-limited price calls while US market shut
            for sym in symbols:
                price = held_price.get(sym)
                if price is None:
                    price = api.get_price(sym, market)
                quotes[f"{market}:{sym}"] = price

    return {
        "now_local": datetime.now(ZoneInfo(config.LOCAL_TZ)).isoformat(),
        "us_market_open": us_open,
        "crypto_market_open": True,
        "account": {
            "cash": round(cash, 2),
            "equity": round(eq["equity"], 2),
            "invested": round(eq["invested"], 2),
            "total_pnl": round(eq["total_pnl"], 2),
            "total_pnl_pct": round(eq["total_pnl_pct"], 3),
            "position_count": eq["position_count"],
            "trades_today": journal.trades_today(),
            "daily_trade_limit": config.DAILY_TRADE_LIMIT,
        },
        "positions": [
            {
                "symbol": p.get("symbol"),
                "market": p.get("market"),
                "side": p.get("side"),
                "quantity": p.get("quantity"),
                "entry_price": p.get("entry_price"),
                "current_price": p.get("current_price"),
                "pnl": p.get("pnl"),
                "pnl_pct": (round((p["pnl"] / (abs(float(p["quantity"])) * float(p["entry_price"]))) * 100, 2)
                            if p.get("pnl") is not None and p.get("entry_price") else None),
                "source": p.get("source"),
            }
            for p in positions
        ],
        "quotes": quotes,
        "hot_movers": hot_movers,
        "universe": config.UNIVERSE,
        "risk": {
            "max_position_pct": config.MAX_POSITION_PCT,
            "max_positions": config.MAX_POSITIONS,
            "cash_reserve_pct": config.CASH_RESERVE_PCT,
            "suggested_trade_pct_range": [config.MIN_TRADE_PCT, config.MAX_TRADE_PCT],
            "stop_loss_pct": config.STOP_LOSS_PCT,
        },
        "market_intel": _market_intel(),
        "recent_journal": journal.recent(6),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(build(), ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
