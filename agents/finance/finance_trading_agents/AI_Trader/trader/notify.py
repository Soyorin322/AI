"""
Discord webhook notifications: per-trade cards and P&L summaries.
Failures here never crash trading — they are logged and swallowed.
"""

import requests

import config

_GREEN = 0x2ECC71
_RED = 0xE74C3C
_BLUE = 0x3498DB
_GREY = 0x95A5A6

_ACTION_LABEL = {
    "buy": "🟢 BUY 买入",
    "sell": "🔴 SELL 卖出",
    "short": "🟠 SHORT 做空",
    "cover": "🔵 COVER 平空",
}


def _post(payload: dict) -> bool:
    try:
        r = requests.post(config.DISCORD_WEBHOOK, json=payload, timeout=15)
        return r.status_code in (200, 204)
    except requests.RequestException as exc:
        print(f"[notify] discord post failed: {exc}")
        return False


def notify_text(title: str, description: str, color: int = _BLUE) -> bool:
    return _post({
        "username": "AI-Trader Bot",
        "embeds": [{"title": title, "description": description, "color": color}],
    })


def notify_trade(action: str, market: str, symbol: str, quantity: float,
                 price: float, rationale: str, cash_after: float,
                 position_after: dict | None) -> bool:
    action = action.lower()
    color = _GREEN if action in ("buy", "cover") else _RED
    notional = price * quantity
    fields = [
        {"name": "市场", "value": market, "inline": True},
        {"name": "数量", "value": f"{quantity:.6g}", "inline": True},
        {"name": "成交价", "value": f"${price:,.4g}", "inline": True},
        {"name": "金额", "value": f"${notional:,.2f}", "inline": True},
        {"name": "成交后现金", "value": f"${cash_after:,.2f}", "inline": True},
    ]
    if position_after:
        pos_qty = position_after.get("quantity")
        pos_side = position_after.get("side", "")
        if pos_qty is not None:
            fields.append({
                "name": "当前持仓",
                "value": f"{pos_side} {abs(float(pos_qty)):.6g} {symbol}",
                "inline": True,
            })
    return _post({
        "username": "AI-Trader Bot",
        "embeds": [{
            "title": f"{_ACTION_LABEL.get(action, action.upper())}  ·  {symbol}",
            "description": rationale or "(no rationale)",
            "color": color,
            "fields": fields,
        }],
    })


def notify_loop_state(on: bool, equity: float | None = None) -> bool:
    if on:
        title = "🟢 自动交易已启动"
        desc = "Claude 引擎已开始按策略自动下单。每笔成交与实时收益会持续推送到此频道。"
        color = _GREEN
    else:
        title = "🔴 自动交易已停止"
        desc = "Claude 引擎已暂停，不再开新仓（已有持仓保留，可随时再启动）。"
        color = _RED
    embed = {"title": title, "description": desc, "color": color}
    if equity is not None:
        embed["fields"] = [{"name": "当前权益", "value": f"${equity:,.2f}", "inline": True}]
    embed["footer"] = {"text": "AI-Trader · 模拟盘 paper trading"}
    return _post({"username": "AI-Trader Bot", "embeds": [embed]})


def notify_pnl(equity: float, cash: float, total_pnl: float,
               total_pnl_pct: float, positions: list[dict]) -> bool:
    color = _GREEN if total_pnl >= 0 else _RED
    sign = "+" if total_pnl >= 0 else ""
    if positions:
        lines = []
        for p in positions:
            pnl = p.get("pnl")
            pnl_str = f"{'+' if (pnl or 0) >= 0 else ''}{pnl:,.2f}" if pnl is not None else "—"
            cur = p.get("current_price")
            cur_str = f"${cur:,.4g}" if cur else "—"
            lines.append(
                f"`{p['symbol']:<5}` {p.get('side','')[:1].upper()} "
                f"{abs(float(p['quantity'])):.4g} @ ${float(p['entry_price']):,.4g} "
                f"→ {cur_str}  (P&L {pnl_str})"
            )
        holdings = "\n".join(lines)
    else:
        holdings = "_无持仓 (all cash)_"
    return _post({
        "username": "AI-Trader Bot",
        "embeds": [{
            "title": "📊 实时收益 / Portfolio P&L",
            "color": color,
            "fields": [
                {"name": "总权益 Equity", "value": f"${equity:,.2f}", "inline": True},
                {"name": "现金 Cash", "value": f"${cash:,.2f}", "inline": True},
                {"name": "总盈亏 P&L",
                 "value": f"{sign}${total_pnl:,.2f} ({sign}{total_pnl_pct:.2f}%)",
                 "inline": True},
                {"name": f"持仓 Holdings ({len(positions)})", "value": holdings, "inline": False},
            ],
            "footer": {"text": "AI-Trader · 模拟盘 paper trading · localhost:8000"},
        }],
    })
