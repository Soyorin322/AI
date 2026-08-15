#!/usr/bin/env python
"""
auto-buy-alert · Discord bot for /eval <ticker>.

Slash command -> defers -> runs eval_data.py (deterministic facts) -> Claude
synthesizes a 全方位 report (eval_routine.md + live news) -> posts it back.

Needs (in .env):  DISCORD_BOT_TOKEN=...   and optionally  DISCORD_GUILD_ID=...
(guild id makes the slash command appear instantly; global sync can take ~1h).
Run: python bot.py
"""
import asyncio
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import discord
from discord import app_commands

HERE = Path(__file__).resolve().parent
CLAUDE_EXE = r"C:\Users\hongy\.local\bin\claude.exe"
KRONOS_SCRIPT = HERE.parent / ".claude" / "skills" / "alphaear-predictor" / "kronos_forecast.py"
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def envval(key):
    v = os.environ.get(key)
    if v:
        return v.strip()
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(key) and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


TOKEN = envval("DISCORD_BOT_TOKEN")
GUILD_ID = envval("DISCORD_GUILD_ID")


def generate_report(ticker):
    """Blocking: gather data + Claude synthesis. Returns (data, report) or (None, err)."""
    try:
        r = subprocess.run([sys.executable, str(HERE / "eval_data.py"), ticker],
                           capture_output=True, text=True, timeout=90, creationflags=NOWIN)
        data = json.loads(r.stdout)
    except Exception as e:
        return None, f"数据获取失败: {str(e)[:80]}"
    if data.get("error"):
        return None, f"找不到 `{ticker}` 的数据(代码对吗?)"
    # Kronos forecast (optional, heavy ~30s model load; never blocks the report)
    try:
        kr = subprocess.run([sys.executable, str(KRONOS_SCRIPT), data.get("ticker", ticker)],
                            capture_output=True, text=True, timeout=200, creationflags=NOWIN)
        lines = (kr.stdout or "").strip().splitlines()
        if lines:
            kd = json.loads(lines[-1])
            if kd.get("ok"):
                data["kronos"] = kd
    except Exception:
        pass
    prompt = ("你是股票/加密评估助手。读取 auto-buy-alert/eval_routine.md 并据此,为下面 JSON 数据生成"
              "一份**中文 Markdown 全方位评估报告**;先用 WebSearch 查该标的近 7–14 天英文新闻/催化。"
              "**只输出报告正文**,不要额外说明。\n\n数据 JSON:\n" + json.dumps(data, ensure_ascii=False))
    try:
        c = subprocess.run(
            [CLAUDE_EXE, "-p", prompt, "--permission-mode", "acceptEdits",
             "--max-budget-usd", "1.5", "--allowedTools", "WebSearch", "WebFetch", "Read"],
            capture_output=True, text=True, timeout=300, creationflags=NOWIN, cwd=str(HERE.parent))
        report = (c.stdout or "").strip()
    except Exception as e:
        return None, f"报告生成失败: {str(e)[:80]}"
    if not report:
        return None, "报告生成失败(Claude 无输出)"
    return data, report


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="eval", description="生成一只美股/加密的全方位评估报告")
@app_commands.describe(ticker="代码,如 INTC / NVDA / TSLA / BTC")
async def eval_cmd(interaction: discord.Interaction, ticker: str):
    await interaction.response.defer(thinking=True)
    data, report = await asyncio.to_thread(generate_report, ticker)
    if data is None:
        await interaction.followup.send(f"⚠️ {report}")
        return
    title = f"📊 {data.get('ticker')} 全方位评估"
    if len(report) <= 4000:
        emb = discord.Embed(title=title, description=report, color=0x2ecc71)
        emb.set_footer(text="⚠️ 仅供参考,非投资建议")
        await interaction.followup.send(embed=emb)
    else:
        f = discord.File(io.BytesIO(report.encode("utf-8")), filename=f"{data.get('ticker')}_eval.md")
        await interaction.followup.send(
            content=f"📊 **{data.get('ticker')} 全方位评估**(完整见附件)\n⚠️ 仅供参考,非投资建议", file=f)


@client.event
async def on_ready():
    print(f"bot logged in as {client.user}; in {len(client.guilds)} guild(s): {[g.name for g in client.guilds]}", flush=True)
    try:
        targets = [discord.Object(id=int(GUILD_ID))] if GUILD_ID else list(client.guilds)
        if targets:
            for g in targets:
                tree.copy_global_to(guild=g)
                await tree.sync(guild=g)
            print(f"/eval synced to {len(targets)} guild(s)", flush=True)
        else:
            await tree.sync()
            print("bot in 0 guilds — add via OAuth2 URL; on_guild_join will sync instantly", flush=True)
    except Exception as e:
        print("command sync error:", e, flush=True)


@client.event
async def on_guild_join(guild):
    # when the bot is added to a server, register /eval there immediately
    try:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"joined guild {guild.name} ({guild.id}); /eval synced", flush=True)
    except Exception as e:
        print("guild-join sync error:", e, flush=True)


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not set in .env")
        sys.exit(2)
    client.run(TOKEN)
