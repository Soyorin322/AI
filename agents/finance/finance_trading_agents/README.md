# Finance Trading Agents

Two self-hosted finance automation projects in one repo:

| Folder | What it is |
|--------|-----------|
| [`AI-Trader/`](AI-Trader/) | A self-hosted fork of [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) (agent-native paper-trading platform: FastAPI backend + React frontend) **plus** a custom LLM-driven auto **paper-trading agent** in [`AI-Trader/trader/`](AI-Trader/trader/) — a swing book (crypto + US stocks) and an aggressive dynamic day-trade book. |
| [`auto-buy-alert/`](auto-buy-alert/) | A stock/ETF momentum **screener + Discord alert bot** (hot-list scan, fund-flow tracker, fear/greed, a small status dashboard). |

> **Everything here is paper trading / alerting only — no real money, no brokerage orders.**

---

## ⚠️ Security — read first

This repo contains **no secrets**. All tokens, passwords, Discord webhooks and API keys live in gitignored files you create locally:

- `AI-Trader/.env`  ← copy from `AI-Trader/.env.example`
- `AI-Trader/trader/secrets.json`  ← copy from `AI-Trader/trader/secrets.json.example`
- `auto-buy-alert/.env`  ← copy from `auto-buy-alert/.env.example`

Never commit those files. The root [`.gitignore`](.gitignore) already excludes them, plus virtualenvs, `node_modules`, databases, logs and runtime state.

---

## Prerequisites

- **Python 3.12** (a venv per project is recommended)
- **Node.js 18+** (only for building the AI-Trader frontend)
- Windows, macOS or Linux. This deployment was run on Windows; a few Windows-specific fixes are noted below.

---

## Part 1 — AI-Trader (platform + trading agent)

### 1a. Backend + frontend (the HKUDS platform)

```bash
cd AI-Trader
python -m venv .venv
# Windows:  .venv\Scripts\activate       Linux/macOS:  source .venv/bin/activate
pip install -r service/requirements.txt

# Fixes this deploy needed on top of upstream requirements:
pip install openrouter email-validator      # requirements pins a nonexistent openrouter>=1.0.0; email-validator is missing
```

- On **Windows**, `service/server/worker.py` imports `fcntl` (Unix-only). This fork makes it optional; if you re-pull upstream, guard that import.

Configure environment:

```bash
cp .env.example .env         # then edit .env
```

- Set `ALPHA_VANTAGE_API_KEY` to a free [Alpha Vantage](https://www.alphavantage.co/support/#api-key) key to enable US-stock market data (`=demo` is treated as unconfigured). Crypto (Hyperliquid) and Polymarket need no key.

Run it:

```bash
python service/server/main.py     # API + UI on http://localhost:8000  (serves the built frontend at /)
python service/server/worker.py   # separate process: live prices / news
```

Frontend (dev with hot-reload, optional — the backend already serves a built copy):

```bash
cd service/frontend
npm install
npm run dev        # http://localhost:3000, proxies /api -> http://localhost:8000
# or: npm run build   -> outputs dist/ which the backend serves at /
```

The database is SQLite at `service/server/data/clawtrader.db` (auto-created; gitignored).

### 1b. The Claude auto-trading agent (`trader/`)

A discretionary, rule-bounded paper-trading agent that runs on top of the local platform. Two independent books selected by the `TRADER_MODE` env var:

- **swing** — crypto (BTC/ETH/SOL) + US stocks, ~30-min cadence, stop −15% / take-profit +20%.
- **day** — US stocks only, ~5-min cadence, **dynamic universe** (pulls the day's top movers from yfinance via `hotscan.py`), highly aggressive (stop −6% / TP +10%, flat by end of day). See [`trader/STRATEGY.md`](AI-Trader/trader/STRATEGY.md) and [`trader/STRATEGY_DAY.md`](AI-Trader/trader/STRATEGY_DAY.md).

Setup:

```bash
# 1) With the platform running, register two agent accounts (one swing, one day-trade)
#    to obtain each agent's id + bearer token.
# 2) Copy the template and fill in the ids/tokens/webhooks:
cp trader/secrets.json.example trader/secrets.json
# 3) Install the agent's extra deps into the same venv:
pip install yfinance requests fastapi uvicorn
```

Everything is driven from the repo root. Prefix day-mode commands with `TRADER_MODE=day`:

```bash
# Read a market + account snapshot (JSON): quotes, positions, P&L, risk, (day: hot_movers)
python trader/snapshot.py
TRADER_MODE=day python trader/snapshot.py

# Place one risk-checked paper trade (Discord-notified + journaled)
python trader/execute.py --action buy  --market crypto   --symbol BTC  --notional 8000 --reason "..."
python trader/execute.py --action sell --market crypto   --symbol BTC  --pct 100        --reason "..."
TRADER_MODE=day python trader/execute.py --action buy --market us-stock --symbol NVDA --notional 9000 --reason "..."

# Push a P&L card to Discord
python trader/report.py

# Web on/off control panel (HTTP Basic auth from secrets.json: panel_user / panel_pass)
python trader/control_server.py            # http://localhost:8799
```

**How the "engine" runs:** each cycle is snapshot → decide → execute → record. `trader/engine.py poll` refreshes a heartbeat and reports whether a cycle is due; `trader/state.py` holds the on/off flag the control panel flips. In this deployment the decision loop is driven by a scheduled LLM (Claude) session, but the same commands can be driven by a cron job or by hand.

**Public panel (optional):** expose the control panel with ngrok — `trader/bin/ngrok.exe http 8799` (download ngrok separately and set your authtoken; `trader/bin/` is gitignored).

---

## Part 2 — auto-buy-alert (screener + Discord alerts)

A lightweight momentum screener that posts buy alerts and fund-flow cards to Discord, plus a small dashboard.

```bash
cd auto-buy-alert
python -m venv .venv        # or reuse a shared venv
pip install requests yfinance pandas python-dotenv

cp .env.example .env        # then set your Discord webhooks / bot token
```

Configure the tickers you track in `watchlist.txt` / `watchlists.json`.

Run the pieces you want:

```bash
python screen.py           # run the screen and push buy alerts to Discord
python hot_list.py         # build the hot-movers list
python fund_tracker.py     # fund-flow cards -> Discord
python fear_greed.py       # fear & greed indicator
python status_server.py    # local status dashboard (http://localhost:8642)
python bot.py              # optional interactive Discord bot (needs DISCORD_BOT_TOKEN)
```

To run it automatically at market sessions on Windows, see `run_alert.ps1` / `run_hidden.vbs` (launch via Task Scheduler). Operating notes are in `run_routine.md` and `eval_routine.md`.

---

## Credits & license

- `AI-Trader/` is a fork of **[HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader)** — see the upstream repo for its license and full platform documentation. The `trader/` agent and the Windows/deploy fixes are added on top.
- `auto-buy-alert/` and `AI-Trader/trader/` are the custom work in this repo.
