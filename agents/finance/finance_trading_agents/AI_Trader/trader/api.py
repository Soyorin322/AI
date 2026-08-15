"""
Thin HTTP client for the AI-Trader backend.

Every call is paper trading against the local instance. Functions return parsed
JSON (or raise RuntimeError with the server's message). The /api/price endpoint
is rate-limited to 1 req/sec/agent, so get_price() self-throttles.
"""

import sys
from datetime import datetime, timezone

import requests

import config

# Reuse the server's own price fetcher so our sizing price matches what the
# trade will fill at (Hyperliquid for crypto, Alpha Vantage/yfinance for stocks).
if config.SERVER_DIR not in sys.path:
    sys.path.insert(0, config.SERVER_DIR)
try:
    import price_fetcher as _pf
except Exception:  # pragma: no cover - pricing falls back to HTTP if unavailable
    _pf = None

_AUTH = {"Authorization": f"Bearer {config.TOKEN}"}


def _url(path: str) -> str:
    return f"{config.API_BASE}{path}"


def agent_me() -> dict:
    r = requests.get(_url("/api/claw/agents/me"), headers=_AUTH,
                     timeout=config.REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()


def get_positions(token: str | None = None) -> dict:
    """Returns {'positions': [...], 'cash': float}. Defaults to this mode's token."""
    headers = {"Authorization": f"Bearer {token}"} if token else _AUTH
    r = requests.get(_url("/api/positions"), headers=headers,
                     timeout=config.REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()


def get_price(symbol: str, market: str):
    """Current quote for symbol/market via the server's price_fetcher, or None."""
    if _pf is None:
        return None
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        price = _pf.get_price_from_market(symbol, now_iso, market)
    except Exception:
        return None
    try:
        price = float(price)
    except (TypeError, ValueError):
        return None
    return price if price and price > 0 else None


def place_trade(action: str, market: str, symbol: str, quantity: float,
                content: str):
    """
    POST /api/signals/realtime. For crypto/us-stock we send price=0 and
    executed_at='now'; the server fills in the real market price.
    Returns the parsed JSON response. Raises RuntimeError on 4xx/5xx with the
    server's detail message.
    """
    body = {
        "market": market,
        "action": action,
        "symbol": symbol,
        "price": 0,
        "quantity": quantity,
        "content": content,
        "executed_at": "now",
    }
    r = requests.post(_url("/api/signals/realtime"), headers=_AUTH, json=body,
                      timeout=config.REQUEST_TIMEOUT_SECONDS)
    if r.status_code != 200:
        detail = r.text
        try:
            detail = r.json().get("detail", detail)
        except ValueError:
            pass
        raise RuntimeError(f"trade rejected ({r.status_code}): {detail}")
    return r.json()


def get_profit_history(limit: int = 50) -> dict:
    r = requests.get(_url("/api/profit/history"), params={"limit": limit},
                     timeout=config.REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()
