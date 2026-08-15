#!/usr/bin/env python
"""
auto-buy-alert · Discord notifier.

Reads DISCORD_WEBHOOK_URL from the environment or from the sibling .env file.
Reads a JSON payload (a single card dict or a list of them) from --file or stdin
and posts them as Discord embeds.

Card schema:
{
  "ticker": "NVDA", "name": "NVIDIA", "price": "210.69", "currency": "USD",
  "confidence": "中", "session_label": "盘后",
  "technical": "...", "news": "...", "risk": "...",
  "color": "green" | "yellow" | "red" | "gray"   # optional, default green
}
A plain message card: {"summary": "今日无买点信号(盘后)", "title": "ℹ️ ..."}
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
COLORS = {"green": 3066993, "yellow": 16776960, "red": 15158332, "gray": 9807270}


def load_webhook(key="DISCORD_WEBHOOK_URL"):
    url = os.environ.get(key)
    if url:
        return url.strip()
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(key) and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def build_embed(card):
    if "summary" in card:
        return {
            "title": card.get("title", "ℹ️ AutoBuyAlert"),
            "description": card["summary"],
            "color": COLORS["gray"],
        }
    color = COLORS.get(card.get("color", "green"), COLORS["green"])
    name = card.get("name", card["ticker"])
    title = f"🟢 买点提醒 · {name} ({card['ticker']})"
    head = f"${card.get('price', '—')} {card.get('currency', 'USD')}".strip()
    if card.get("confidence"):
        head += f"  ·  置信度:{card['confidence']}"
    if card.get("session_label"):
        head += f"  ·  {card['session_label']}"
    fields = [{"name": "现价 / 置信度", "value": head or "—", "inline": False}]
    if card.get("technical"):
        fields.append({"name": "📈 技术面", "value": card["technical"][:1000], "inline": False})
    if card.get("news"):
        fields.append({"name": "📰 新闻/情绪", "value": card["news"][:1000], "inline": False})
    if card.get("risk"):
        fields.append({"name": "⚠️ 风险", "value": card["risk"][:1000], "inline": False})
    return {"title": title, "color": color, "fields": fields,
            "footer": {"text": "⚠️ 仅供参考,非投资建议"}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="JSON file; if omitted, read stdin")
    ap.add_argument("--username", default="BuyAlertBot")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the Discord payload instead of sending it")
    ap.add_argument("--mention", action="store_true",
                    help="prepend @everyone and allow the ping (use for real alerts)")
    ap.add_argument("--webhook-key", default="DISCORD_WEBHOOK_URL",
                    help="which .env webhook to use (e.g. DISCORD_WEBHOOK_FUNDS)")
    args = ap.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8-sig") if args.file else sys.stdin.read()
    data = json.loads(raw)
    cards = data if isinstance(data, list) else [data]

    embeds = [build_embed(c) for c in cards]

    def elen(e):
        n = len(e.get("title", "")) + len(e.get("description", ""))
        for f in e.get("fields", []):
            n += len(f.get("name", "")) + len(f.get("value", ""))
        n += len(e.get("footer", {}).get("text", ""))
        return n

    # Discord limits: <=10 embeds and ~6000 chars per message -> chunk on both.
    groups, cur, curlen = [], [], 0
    for e in embeds:
        el = elen(e)
        if cur and (len(cur) >= 10 or curlen + el > 5500):
            groups.append(cur)
            cur, curlen = [], 0
        cur.append(e)
        curlen += el
    if cur:
        groups.append(cur)

    payloads = []
    for gi, g in enumerate(groups):
        p = {"username": args.username, "embeds": g}
        if args.mention and gi == 0:
            p["content"] = "@everyone"
            p["allowed_mentions"] = {"parse": ["everyone"]}
        payloads.append(p)

    if args.dry_run:
        print(json.dumps(payloads, ensure_ascii=False, indent=2))
        sys.exit(0)

    url = load_webhook(args.webhook_key)
    if not url:
        print(f"ERROR: {args.webhook_key} not found (env or .env)", file=sys.stderr)
        sys.exit(2)

    ok = True
    for p in payloads:
        r = requests.post(url, json=p, timeout=20)
        print(f"HTTP {r.status_code}")
        if r.status_code not in (200, 204):
            ok = False
            print(r.text[:300], file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
