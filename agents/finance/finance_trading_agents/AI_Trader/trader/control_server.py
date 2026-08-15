"""
Control panel for the Claude auto paper-trading agent.

  python trader/control_server.py     ->  http://localhost:8787

Serves the toggle page and a small JSON API. The page flips loop_on; the Claude
Code session (the engine) reads that flag each wake and trades when it is on.
This server never trades — it only reflects state + account, and writes the flag.
"""

import asyncio
import base64
import hmac
import time
from datetime import datetime, timezone

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

import config
import api
import journal
import notify
import portfolio
import state

ALERT_UPSTREAM = "http://127.0.0.1:8642"  # the user's auto-buy-alert dashboard

HERE = config.HERE
PAGE = f"{HERE}/control.html"
ENGINE_ONLINE_MAX_AGE_SECONDS = 40 * 60  # heartbeat older than this => session not running

_acct_cache = {}  # mode -> (ts, data)
_ACCT_TTL = 12.0

app = FastAPI(title="Claude Trader Control")


@app.middleware("http")
async def basic_auth(request: Request, call_next):
    """Protect the whole panel with HTTP Basic Auth when a password is set."""
    if config.PANEL_PASS:
        ok = False
        header = request.headers.get("authorization", "")
        if header.startswith("Basic "):
            try:
                user, _, pw = base64.b64decode(header[6:]).decode("utf-8").partition(":")
                ok = (hmac.compare_digest(user, config.PANEL_USER)
                      and hmac.compare_digest(pw, config.PANEL_PASS))
            except Exception:  # noqa: BLE001
                ok = False
        if not ok:
            return Response(status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="Claude Trader"'})
    return await call_next(request)


def _engine_online(heartbeat: str | None) -> bool:
    if not heartbeat:
        return False
    try:
        hb = datetime.strptime(heartbeat, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - hb).total_seconds() < ENGINE_ONLINE_MAX_AGE_SECONDS


def _account(mode: str) -> dict:
    now = time.time()
    cached = _acct_cache.get(mode)
    if cached and now - cached[0] < _ACCT_TTL:
        return cached[1]
    token = config.MODES[mode]["token"]
    try:
        pos_data = api.get_positions(token=token)
        positions = portfolio.enrich_live(pos_data.get("positions", []))
        cash = float(pos_data.get("cash", config.INITIAL_CAPITAL))
        eq = portfolio.snapshot_equity(positions, cash)
        out = {
            "cash": round(cash, 2),
            "equity": round(eq["equity"], 2),
            "total_pnl": round(eq["total_pnl"], 2),
            "total_pnl_pct": round(eq["total_pnl_pct"], 3),
            "position_count": eq["position_count"],
            "positions": [
                {
                    "symbol": p.get("symbol"), "side": p.get("side"),
                    "quantity": p.get("quantity"), "entry_price": p.get("entry_price"),
                    "current_price": p.get("current_price"), "pnl": p.get("pnl"),
                    "pnl_pct": (round((p["pnl"] / (abs(float(p["quantity"])) * float(p["entry_price"]))) * 100, 2)
                                if p.get("pnl") is not None and p.get("entry_price") else None),
                }
                for p in positions
            ],
        }
    except Exception as exc:  # noqa: BLE001
        out = {"error": str(exc), "positions": []}
    _acct_cache[mode] = (now, out)
    return out


def _mode_status(mode: str) -> dict:
    s = state.load(mode)
    recent = [e for e in journal.recent(40, mode=mode) if e.get("event") == "trade"][-12:][::-1]
    return {
        "label": config.MODES[mode]["label"],
        "loop_on": s.get("loop_on", False),
        "engine_heartbeat": s.get("engine_heartbeat"),
        "engine_online": _engine_online(s.get("engine_heartbeat")),
        "last_cycle_at": s.get("last_cycle_at"),
        "cycle_count": s.get("cycle_count", 0),
        "interval_minutes": config.MODES[mode]["interval_minutes"],
        "account": _account(mode),
        "recent_trades": recent,
    }


@app.get("/")
async def index():
    return FileResponse(PAGE)


@app.get("/api/status")
async def status():
    swing = await asyncio.to_thread(_mode_status, "swing")
    day = await asyncio.to_thread(_mode_status, "day")
    return JSONResponse({"modes": {"swing": swing, "day": day}})


def _announce_webhook(mode: str, on: bool, equity) -> None:
    wh = config.MODES[mode]["webhook"]
    if not wh:
        return
    label = config.MODES[mode]["label"]
    color = 0x2ECC71 if on else 0xE74C3C
    title = (f"🟢 {label} · 自动交易已启动" if on
             else f"🔴 {label} · 自动交易已停止")
    desc = ("引擎已开始按策略自动下单，成交与收益将持续推送到此频道。" if on
            else "引擎已暂停，不再开新仓（已有持仓保留）。")
    embed = {"title": title, "description": desc, "color": color,
             "footer": {"text": "AI-Trader · 模拟盘 paper trading"}}
    if equity is not None:
        embed["fields"] = [{"name": "当前权益", "value": f"${equity:,.2f}", "inline": True}]
    try:
        requests.post(wh, json={"username": "AI-Trader Bot", "embeds": [embed]}, timeout=10)
    except requests.RequestException:
        pass


async def _apply_toggle(mode: str, new_on: bool) -> None:
    state.set_loop(new_on, mode)
    acct = await asyncio.to_thread(_account, mode)
    await asyncio.to_thread(_announce_webhook, mode, new_on, acct.get("equity"))


@app.post("/api/toggle/{mode}")
async def toggle(mode: str):
    if mode not in config.MODES:
        return JSONResponse({"error": "unknown mode"}, status_code=404)
    new_on = not state.load(mode).get("loop_on", False)
    await _apply_toggle(mode, new_on)
    return JSONResponse({"mode": mode, "loop_on": new_on})


@app.post("/api/set/{mode}")
async def set_state(mode: str, payload: dict):
    if mode not in config.MODES:
        return JSONResponse({"error": "unknown mode"}, status_code=404)
    prev = state.load(mode).get("loop_on", False)
    new_on = bool(payload.get("loop_on"))
    if new_on != prev:
        await _apply_toggle(mode, new_on)
    return JSONResponse({"mode": mode, "loop_on": new_on})


# ==================== auto-buy-alert (:8642) reverse proxy ====================
# Lets the 8642 dashboard be embedded in the panel and reached through the same
# authenticated public URL. Its inline JS polls root-relative /api/* — we rewrite
# those to /alert/api/* and proxy them back to 8642.

def _fetch_alert(path: str, params=None):
    return requests.get(f"{ALERT_UPSTREAM}/{path}", params=params or {}, timeout=8)


@app.get("/alert")
@app.get("/alert/")
async def alert_root():
    try:
        r = await asyncio.to_thread(_fetch_alert, "")
    except requests.RequestException as exc:
        return HTMLResponse(
            f"<body style='background:#0d1117;color:#e6edf3;font-family:sans-serif;padding:24px'>"
            f"<h3>auto-buy-alert 未运行</h3><p>无法连接 127.0.0.1:8642：{exc}</p></body>",
            status_code=502)
    html = (r.text
            .replace("fetch('/api", "fetch('/alert/api")
            .replace('fetch("/api', 'fetch("/alert/api')
            .replace("fetch(`/api", "fetch(`/alert/api"))
    return HTMLResponse(html, status_code=r.status_code)


@app.get("/alert/{path:path}")
async def alert_proxy(path: str, request: Request):
    try:
        r = await asyncio.to_thread(_fetch_alert, path, dict(request.query_params))
    except requests.RequestException as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
    return Response(content=r.content, status_code=r.status_code,
                    media_type=r.headers.get("content-type", "application/octet-stream"))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8799, access_log=False)
