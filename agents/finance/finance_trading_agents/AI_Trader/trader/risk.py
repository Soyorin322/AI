"""
Risk guardrails. Every order passes through evaluate() before it is sent.
Works in notional dollars; execute.py converts to quantity via current price.

For buy/short the allowed notional may be clamped down to satisfy the caps;
if nothing is allowed (or a rule is violated) ok=False with a reason.
"""

import config
import portfolio

_FEE_BUFFER = 0.01  # 1% cash headroom to cover trading fees


def evaluate(action: str, market: str, symbol: str, target_notional: float,
             positions: list[dict], cash: float, equity: float,
             trades_today: int) -> dict:
    action = action.lower()
    symbol = symbol.upper()

    held = [p for p in positions if (p.get("symbol") or "").upper() == symbol]

    # Exits are ALWAYS allowed (if held): risk-management closes must never be
    # blocked by the universe whitelist or the daily trade cap — otherwise a name
    # that drops off the dynamic movers board, or hitting the day's trade limit,
    # could trap a losing position past its stop.
    if action in ("sell", "cover"):
        if not held:
            return _no(f"没有 {symbol} 的持仓可平")
        return {"ok": True, "reason": "ok", "allowed_notional": target_notional}

    if action not in ("buy", "short"):
        return _no(f"未知操作 {action}")

    # ---- new-exposure gates (buy/short only) ----
    if symbol not in config.UNIVERSE.get(market, []):
        return _no(f"{symbol} 不在 {market} 标的池内")

    if trades_today >= config.DAILY_TRADE_LIMIT:
        return _no(f"已达单日交易上限 ({config.DAILY_TRADE_LIMIT})")

    if target_notional <= 0:
        return _no("下单金额必须为正")

    # New-position count cap
    if not held and len(positions) >= config.MAX_POSITIONS:
        return _no(f"已持有 {len(positions)} 个仓位，达上限 {config.MAX_POSITIONS}")

    # Per-symbol exposure cap
    max_symbol = config.MAX_POSITION_PCT * equity
    room_symbol = max_symbol - portfolio.symbol_exposure(positions, symbol)

    # Cash reserve cap
    reserve = config.CASH_RESERVE_PCT * equity
    room_cash = (cash - reserve) / (1 + _FEE_BUFFER)

    allowed = min(target_notional, room_symbol, room_cash)

    if allowed < 1:
        if room_symbol <= 0:
            return _no(f"{symbol} 已达单仓上限 {config.MAX_POSITION_PCT:.0%} 权益")
        return _no(f"现金不足（需保留 {config.CASH_RESERVE_PCT:.0%} 储备）")

    return {
        "ok": True,
        "reason": ("ok" if allowed >= target_notional - 1
                   else f"按风控上限缩减至 ${allowed:,.0f}"),
        "allowed_notional": allowed,
    }


def _no(reason: str) -> dict:
    return {"ok": False, "reason": reason, "allowed_notional": 0.0}
