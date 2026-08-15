"""
Shared configuration for the Claude auto paper-trading agents.

Two independent modes, selected by the TRADER_MODE env var (default "swing"):
  - swing : the original position/swing book (crypto + US stock, 30-min cadence)
  - day   : an aggressive intraday US-stock book (~5-min cadence, tight stops)

Each mode has its own agent token, Discord webhook, universe, risk guardrails,
state file and journal — fully separate accounts. Secrets live in secrets.json
(gitignored). Everything is paper trading — no real money.
"""

import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(HERE, "secrets.json")
SERVER_DIR = os.path.join(os.path.dirname(HERE), "service", "server")

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    _secrets = json.load(f)

# ---- global (mode-independent) ----
API_BASE = _secrets["api_base"].rstrip("/")
ALPHA_VANTAGE_KEY = _secrets.get("alpha_vantage_key", "")
PANEL_USER = _secrets.get("panel_user", "claude")
PANEL_PASS = _secrets.get("panel_pass", "")
INITIAL_CAPITAL = 100_000.0
LOCAL_TZ = "America/Vancouver"
PRICE_MIN_INTERVAL_SECONDS = 1.1
REQUEST_TIMEOUT_SECONDS = 20

if ALPHA_VANTAGE_KEY:
    os.environ.setdefault("ALPHA_VANTAGE_API_KEY", ALPHA_VANTAGE_KEY)
os.environ.setdefault("PRICE_FETCH_VERBOSE", "false")  # keep JSON stdout clean

# ==================== Per-mode definitions ====================
MODES = {
    "swing": {
        "label": "摆动盘 Swing",
        "token": _secrets["token"],
        "agent_id": _secrets["agent_id"],
        "agent_name": _secrets["agent_name"],
        "webhook": _secrets["discord_webhook"],
        "universe": {"crypto": ["BTC", "ETH", "SOL"],
                     "us-stock": ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN"]},
        "max_position_pct": 0.20, "max_positions": 6, "cash_reserve_pct": 0.15,
        "min_trade_pct": 0.05, "max_trade_pct": 0.15,
        "stop_loss_pct": 0.15, "take_profit_pct": 0.20, "daily_trade_limit": 20,
        "interval_minutes": 30, "flat_by_eod": False,
        "state_file": "state.json", "journal_file": "journal.jsonl",
    },
    "day": {
        "label": "日内 Day-Trade",
        "token": _secrets.get("day_token", ""),
        "agent_id": _secrets.get("day_agent_id"),
        "agent_name": _secrets.get("day_agent_name", "claude-daytrader"),
        "webhook": _secrets.get("day_discord_webhook", ""),
        # Dynamic "追热点": the live universe is the yfinance movers board cached
        # in day_universe.json (see hotscan.py). This list is only the liquid
        # CORE fallback used when the cache is missing/stale or the market is shut.
        "universe": {"us-stock": ["NVDA", "TSLA", "AAPL", "AMZN", "META", "AMD"]},
        # Highly aggressive intraday profile.
        "max_position_pct": 0.25, "max_positions": 7, "cash_reserve_pct": 0.10,
        "min_trade_pct": 0.08, "max_trade_pct": 0.20,
        "stop_loss_pct": 0.06, "take_profit_pct": 0.10, "daily_trade_limit": 80,
        "interval_minutes": 5, "flat_by_eod": True,
        "state_file": "state_day.json", "journal_file": "journal_day.jsonl",
    },
}

def _day_universe(core_fallback: list[str]) -> dict:
    """Day-mode live universe = cached yfinance movers (hotscan) ∪ core fallback.

    Reads only day_universe.json (no network — hotscan.refresh() keeps it warm),
    so even a bare `engine.py poll` stays lightweight. Falls back to the liquid
    core list when the cache is missing or stale (>45 min, e.g. market shut)."""
    path = os.path.join(HERE, "day_universe.json")
    tickers: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ts = datetime.strptime(data["generated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
        if (datetime.now(timezone.utc) - ts).total_seconds() / 60 <= 45:
            tickers = [t.upper() for t in (data.get("tickers") or [])]
    except (OSError, ValueError, KeyError):
        tickers = []
    merged = sorted(set(tickers) | {s.upper() for s in core_fallback})
    return {"us-stock": merged}


MODE = os.getenv("TRADER_MODE", "swing").strip().lower()
if MODE not in MODES:
    MODE = "swing"
_M = MODES[MODE]

# ---- selected-mode values (what the rest of the toolkit reads) ----
MODE_LABEL = _M["label"]
TOKEN = _M["token"]
AGENT_ID = _M["agent_id"]
AGENT_NAME = _M["agent_name"]
DISCORD_WEBHOOK = _M["webhook"]
UNIVERSE = _day_universe(_M["universe"]["us-stock"]) if MODE == "day" else _M["universe"]
MAX_POSITION_PCT = _M["max_position_pct"]
MAX_POSITIONS = _M["max_positions"]
CASH_RESERVE_PCT = _M["cash_reserve_pct"]
MIN_TRADE_PCT = _M["min_trade_pct"]
MAX_TRADE_PCT = _M["max_trade_pct"]
STOP_LOSS_PCT = _M["stop_loss_pct"]
TAKE_PROFIT_PCT = _M["take_profit_pct"]
DAILY_TRADE_LIMIT = _M["daily_trade_limit"]
INTERVAL_MINUTES = _M["interval_minutes"]
FLAT_BY_EOD = _M["flat_by_eod"]
JOURNAL_PATH = os.path.join(HERE, _M["journal_file"])
STATE_PATH = os.path.join(HERE, _M["state_file"])
