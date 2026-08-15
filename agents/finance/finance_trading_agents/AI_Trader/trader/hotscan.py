"""
Hot-spot scanner for the day-trade book — the "追热点" data source.

Pulls live intraday movers from yfinance's predefined screeners (free, no API
key, no 25/day cap — unlike Alpha Vantage), applies liquidity guardrails so we
chase tradeable names (not illiquid penny pumps), ranks by intraday momentum,
and caches the board to day_universe.json.

  python trader/hotscan.py            -> refresh + print the board as JSON
  hotscan.refresh()                   -> network scan, write cache, return board
  hotscan.load_tickers(max_age_min)   -> read cache tickers (no network)

config.py reads the cache (load_tickers) to build the day-mode UNIVERSE; only
snapshot.py triggers a refresh() each cycle. Keeping the network call in one
place (and config reading only the file) avoids hammering yfinance per command.
"""

import json
import os
from datetime import datetime, timezone

import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, "day_universe.json")

# ---- liquidity guardrails (even "highly aggressive" must be fillable) ----
MIN_PRICE = 10.0           # avoid sub-$10 penny/illiquid names
MIN_MARKET_CAP = 2_000_000_000     # >= $2B market cap
MIN_VOLUME = 1_000_000     # >= 1M shares traded
MIN_DOLLAR_VOL = 50_000_000        # >= $50M traded today
TOP_N = 12                 # keep the strongest dozen movers
# Predefined yfinance screeners to merge (gainers = momentum longs; actives =
# where the volume/attention is). day_losers intentionally omitted (long-only).
SCREENERS = ("day_gainers", "most_actives")


def _passes(q: dict) -> bool:
    if (q.get("quoteType") or "").upper() != "EQUITY":
        return False
    price = q.get("regularMarketPrice") or 0
    vol = q.get("regularMarketVolume") or 0
    cap = q.get("marketCap") or 0
    if price < MIN_PRICE or vol < MIN_VOLUME or cap < MIN_MARKET_CAP:
        return False
    if price * vol < MIN_DOLLAR_VOL:
        return False
    return True


def _scan_raw() -> list[dict]:
    """Merge the screeners into a deduped, filtered, momentum-ranked board."""
    seen: dict[str, dict] = {}
    for body in SCREENERS:
        try:
            res = yf.screen(body, count=25)
        except Exception:
            continue
        quotes = res.get("quotes", []) if isinstance(res, dict) else (res or [])
        for q in quotes:
            sym = (q.get("symbol") or "").upper()
            if not sym or not _passes(q):
                continue
            row = {
                "ticker": sym,
                "price": round(float(q.get("regularMarketPrice") or 0), 4),
                "chg_pct": round(float(q.get("regularMarketChangePercent") or 0), 2),
                "volume": int(q.get("regularMarketVolume") or 0),
                "market_cap": int(q.get("marketCap") or 0),
            }
            # keep the higher-%change record if a symbol appears in both screeners
            if sym not in seen or row["chg_pct"] > seen[sym]["chg_pct"]:
                seen[sym] = row
    board = sorted(seen.values(), key=lambda r: r["chg_pct"], reverse=True)
    return board[:TOP_N]


def refresh() -> dict:
    """Run the scan, write the cache, and return {generated_at, tickers, board}."""
    board = _scan_raw()
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tickers": [r["ticker"] for r in board],
        "board": board,
    }
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
    return payload


def load(max_age_min: float = 45) -> dict | None:
    """Return the cached payload if present and younger than max_age_min, else None."""
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        ts = datetime.strptime(data["generated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - ts).total_seconds() / 60
        if age <= max_age_min and data.get("tickers"):
            return data
    except (OSError, ValueError, KeyError):
        pass
    return None


def load_tickers(max_age_min: float = 45) -> list[str]:
    data = load(max_age_min)
    return list(data["tickers"]) if data else []


if __name__ == "__main__":
    print(json.dumps(refresh(), ensure_ascii=False, indent=2))
