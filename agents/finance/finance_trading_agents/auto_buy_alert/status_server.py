#!/usr/bin/env python
"""
auto-buy-alert · local status dashboard server.

Binds to 127.0.0.1 only (never exposed to the network — it can read the Discord
webhook for the health check). Serves:
  GET /            -> dashboard.html
  GET /api/status  -> tasks state / last run / next run / today's sessions / log tail
  GET /api/health  -> live connectivity probe: claude.exe, Yahoo Finance, Discord webhook
                      (probe only — never sends a Discord message, never spends tokens)

Run: pythonw status_server.py   (or python for a console)
"""
import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8642
CLAUDE_EXE = r"C:\Users\hongy\.local\bin\claude.exe"


def load_webhook():
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DISCORD_WEBHOOK_URL") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("DISCORD_WEBHOOK_URL")


def query_tasks():
    cmd = r"""
$ts = Get-ScheduledTask -TaskName 'AutoBuyAlert-*' -ErrorAction SilentlyContinue
$out = foreach ($t in $ts) {
  $i = $t | Get-ScheduledTaskInfo
  [pscustomobject]@{
    name       = $t.TaskName
    state      = [string]$t.State
    lastRun    = if ($i.LastRunTime)  { $i.LastRunTime.ToString("s") }  else { $null }
    lastResult = $i.LastTaskResult
    nextRun    = if ($i.NextRunTime)  { $i.NextRunTime.ToString("s") }  else { $null }
  }
}
$out | ConvertTo-Json -Depth 4
"""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        out = (r.stdout or "").strip()
        if not out:
            return []
        data = json.loads(out)
        return [data] if isinstance(data, dict) else data
    except Exception as e:
        return {"error": str(e)[:160]}


def load_watchlists():
    wl = HERE / "watchlists.json"
    if wl.exists():
        try:
            return json.loads(wl.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    return {}


def load_funds_status():
    fs = HERE / "fund_state"
    info = {}
    sa = fs / "sa_13f.json"
    if sa.exists():
        try:
            d = json.loads(sa.read_text(encoding="utf-8"))
            info["sa_13f_date"] = d.get("date")
            info["sa_holdings"] = len(d.get("holdings", {}))
            top = sorted(d.get("holdings", {}).values(), key=lambda x: x.get("value", 0), reverse=True)[:5]
            info["sa_top"] = [h.get("name") for h in top]
        except Exception:
            pass
    ark = fs / "ark_ARKK.json"
    if ark.exists():
        try:
            info["ark_date"] = json.loads(ark.read_text(encoding="utf-8")).get("date")
        except Exception:
            pass
    return info


def build_status():
    last_run = {}
    p = HERE / "last_run.json"
    if p.exists():
        try:
            last_run = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    logs = []
    lp = HERE / "run.log"
    if lp.exists():
        try:
            logs = lp.read_text(encoding="utf-8", errors="replace").splitlines()[-20:]
        except Exception:
            pass
    return {
        "now": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tasks": query_tasks(),
        "watchlists": load_watchlists(),
        "funds": load_funds_status(),
        "last_run": last_run,
        "logs": logs,
    }


def build_market():
    """Fear & Greed indices (US stocks + crypto), via fear_greed.py."""
    try:
        r = subprocess.run([sys.executable, str(HERE / "fear_greed.py")],
                           capture_output=True, text=True, timeout=25,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        return json.loads(r.stdout) if r.stdout.strip() else {"error": "no output"}
    except Exception as e:
        return {"error": str(e)[:120]}


def check_claude():
    try:
        r = subprocess.run([CLAUDE_EXE, "--version"], capture_output=True, text=True, timeout=12,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr).strip()[:80]}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:80]}


def check_yahoo():
    try:
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=8,
        )
        return {"ok": r.status_code == 200, "detail": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:80]}


def check_discord():
    url = load_webhook()
    if not url:
        return {"ok": False, "detail": "no webhook configured"}
    try:
        r = requests.get(url, timeout=8)
        name = ""
        try:
            name = r.json().get("name", "")
        except Exception:
            pass
        return {"ok": r.status_code == 200, "detail": f"HTTP {r.status_code}" + (f" · {name}" if name else "")}
    except Exception as e:
        return {"ok": False, "detail": str(e)[:80]}


def build_health():
    return {
        "checked_at": time.strftime("%H:%M:%S"),
        "claude": check_claude(),
        "yahoo": check_yahoo(),
        "discord": check_discord(),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html", "/dashboard.html"):
            f = HERE / "dashboard.html"
            if f.exists():
                self._send(200, f.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, "dashboard.html missing", "text/plain")
        elif path == "/api/status":
            self._send(200, json.dumps(build_status(), ensure_ascii=False))
        elif path == "/api/health":
            self._send(200, json.dumps(build_health(), ensure_ascii=False))
        elif path == "/api/market":
            self._send(200, json.dumps(build_market(), ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *args):
        pass  # keep it quiet


def main():
    try:
        srv = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        # already running (port in use) -> just exit quietly
        print(f"dashboard not started ({e}); maybe already running on {HOST}:{PORT}")
        return
    print(f"auto-buy-alert dashboard running: http://{HOST}:{PORT}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
