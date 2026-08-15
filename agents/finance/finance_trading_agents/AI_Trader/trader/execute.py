"""
Place ONE risk-checked paper trade, notify Discord, and journal it.

Examples:
  python trader/execute.py --action buy  --market crypto   --symbol BTC --notional 8000 --reason "动量转强，资金费率中性"
  python trader/execute.py --action sell --market crypto   --symbol BTC --pct 100        --reason "触及止盈，落袋"
  python trader/execute.py --action buy  --market us-stock --symbol NVDA --notional 6000 --reason "AI 需求强劲"

Output: a JSON line describing the result (ok / rejected + details).
"""

import argparse
import json
import sys

import api
import config
import journal
import notify
import portfolio


def _round_qty(qty: float, market: str) -> float:
    return round(qty, 6) if market == "crypto" else round(qty, 4)


def _find_position(positions, symbol):
    for p in positions:
        if (p.get("symbol") or "").upper() == symbol.upper():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", required=True, choices=["buy", "sell", "short", "cover"])
    ap.add_argument("--market", required=True, choices=["crypto", "us-stock"])
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--reason", required=True, help="rationale shown in Discord + journal")
    ap.add_argument("--notional", type=float, help="target $ size (buy/short)")
    ap.add_argument("--qty", type=float, help="explicit quantity (overrides notional/pct)")
    ap.add_argument("--pct", type=float, default=100.0, help="percent of held to close (sell/cover)")
    args = ap.parse_args()

    action, market, symbol = args.action, args.market, args.symbol.upper()

    pos_data = api.get_positions()
    positions = pos_data.get("positions", [])
    cash = float(pos_data.get("cash", config.INITIAL_CAPITAL))
    eq = portfolio.snapshot_equity(positions, cash)["equity"]
    held = _find_position(positions, symbol)

    # ---- sizing ----
    if action in ("buy", "short"):
        if args.qty is None and args.notional is None:
            return _out({"ok": False, "stage": "args", "reason": "buy/short 需要 --notional 或 --qty"})
        target_notional = args.notional if args.notional is not None else None
        if target_notional is None:
            price = api.get_price(symbol, market)
            if not price:
                return _reject(action, market, symbol, "无法获取价格（美股需 Alpha Vantage key 且在盘中）", args.reason)
            target_notional = args.qty * price

        risk = __import__("risk").evaluate(
            action, market, symbol, target_notional, positions, cash, eq, journal.trades_today())
        if not risk["ok"]:
            return _reject(action, market, symbol, risk["reason"], args.reason)

        price = api.get_price(symbol, market)
        if not price:
            return _reject(action, market, symbol, "无法获取价格（美股需 Alpha Vantage key 且在盘中）", args.reason)
        qty = args.qty if args.qty is not None else risk["allowed_notional"] / price
        qty = _round_qty(qty, market)
        if qty <= 0:
            return _reject(action, market, symbol, "计算数量过小", args.reason)
        clamp_note = risk["reason"] if risk["reason"] != "ok" else None
    else:  # sell / cover
        risk = __import__("risk").evaluate(
            action, market, symbol, 0, positions, cash, eq, journal.trades_today())
        if not risk["ok"]:
            return _reject(action, market, symbol, risk["reason"], args.reason)
        held_qty = abs(float(held["quantity"]))
        qty = args.qty if args.qty is not None else held_qty * (args.pct / 100.0)
        qty = _round_qty(min(qty, held_qty), market)
        if qty <= 0:
            return _reject(action, market, symbol, "无可平数量", args.reason)
        clamp_note = None

    # ---- place ----
    try:
        resp = api.place_trade(action, market, symbol, qty, args.reason)
    except RuntimeError as exc:
        return _reject(action, market, symbol, str(exc), args.reason)

    fill_price = float(resp.get("price") or 0) or None
    after = api.get_positions()
    cash_after = float(after.get("cash", cash))
    pos_after = _find_position(after.get("positions", []), symbol)

    notify.notify_trade(action, market, symbol, qty, fill_price or 0.0,
                        args.reason, cash_after, pos_after)

    entry = {
        "event": "trade", "action": action, "market": market, "symbol": symbol,
        "quantity": qty, "fill_price": fill_price,
        "notional": round((fill_price or 0) * qty, 2),
        "reason": args.reason, "signal_id": resp.get("signal_id"),
        "points_earned": resp.get("points_earned"), "cash_after": round(cash_after, 2),
    }
    journal.record(entry)
    return _out({"ok": True, **entry, "clamp_note": clamp_note})


def _reject(action, market, symbol, reason, rationale):
    journal.record({"event": "rejected", "action": action, "market": market,
                    "symbol": symbol, "reason": reason, "rationale": rationale})
    return _out({"ok": False, "stage": "risk_or_server", "action": action,
                 "market": market, "symbol": symbol, "reason": reason})


def _out(obj: dict) -> int:
    print(json.dumps(obj, ensure_ascii=False))
    return 0 if obj.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
