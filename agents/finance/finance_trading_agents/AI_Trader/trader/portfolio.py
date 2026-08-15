"""
Portfolio math shared by execute.py (risk sizing) and report.py (P&L).

Mark-to-market valuation matches the server's accounting:
- long  position value  = current_price * qty
- short position value  = (2*entry_price - current_price) * qty   (cover credit)
If current_price is missing we fall back to entry_price.
"""

import config


def enrich_live(positions: list[dict]) -> list[dict]:
    """Mark each position to the live price so P&L is real-time, not worker-lagged."""
    import api  # lazy to avoid import cycles
    for p in positions:
        cur = api.get_price(p.get("symbol"), p.get("market"))
        if not cur:
            continue
        qty = abs(float(p.get("quantity") or 0))
        entry = float(p.get("entry_price") or 0)
        p["current_price"] = cur
        if (p.get("side") or "long").lower() == "short":
            p["pnl"] = (entry - cur) * qty
        else:
            p["pnl"] = (cur - entry) * qty
    return positions


def position_value(pos: dict) -> float:
    qty = abs(float(pos.get("quantity") or 0))
    entry = float(pos.get("entry_price") or 0)
    current = pos.get("current_price")
    current = float(current) if current else entry
    if (pos.get("side") or "long").lower() == "short":
        return (2 * entry - current) * qty
    return current * qty


def snapshot_equity(positions: list[dict], cash: float) -> dict:
    invested = sum(position_value(p) for p in positions)
    equity = cash + invested
    total_pnl = equity - config.INITIAL_CAPITAL
    total_pnl_pct = (total_pnl / config.INITIAL_CAPITAL) * 100 if config.INITIAL_CAPITAL else 0.0
    return {
        "cash": cash,
        "invested": invested,
        "equity": equity,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "position_count": len(positions),
    }


def symbol_exposure(positions: list[dict], symbol: str) -> float:
    return sum(position_value(p) for p in positions
              if (p.get("symbol") or "").upper() == symbol.upper())
