# bot.py — LLM-enabled Discord bot that always answers like a pirate ☠️🏴‍☠️
import os
from typing import List

import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv

# ---------- env ----------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in .env")
if not OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY not set — /ask and !ask will answer with an error.")

# ---------- discord ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- openai (async) ----------
from openai import AsyncOpenAI
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Pirate “system” persona: clear, helpful, but swashbucklin’.
PIRATE_SYSTEM_PROMPT = (
    "Ye be ChatGPT, but speak as a cheerful pirate. "
    "Use nautical slang lightly (‘Arrr’, ‘matey’, ‘aye’) while staying clear and helpful. "
    "Keep answers concise unless detail is requested. Avoid offensive stereotypes."
)

async def llm_complete(user_prompt: str) -> str:
    if not ai_client:
        return "Arrr! Me spyglass sees no OPENAI_API_KEY in yer bilge (.env)."
    try:
        resp = await ai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": PIRATE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"Blimey! The LLM coughed up a squall: {e}"

def chunk(text: str, limit: int = 1900) -> List[str]:
    parts, buf, count = [], [], 0
    for word in text.split():
        if count + len(word) + 1 > limit:
            parts.append(" ".join(buf))
            buf, count = [word], len(word) + 1
        else:
            buf.append(word); count += len(word) + 1
    if buf: parts.append(" ".join(buf))
    return parts or ["(no content)"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} app commands")
    except Exception as e:
        print(f"Slash sync failed: {e}")

# ---------- Slash: /ask ----------
@bot.tree.command(name="ask", description="Ask the piratey LLM, arrr!")
@app_commands.describe(prompt="What be yer question, matey?")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    answer = await llm_complete(prompt)
    for i, part in enumerate(chunk(answer)):
        if i == 0: await interaction.followup.send(part)
        else: await interaction.followup.send(part)

# ---------- Prefix: !ask ----------
@bot.command(name="ask", help="Ask the piratey LLM, e.g. !ask How tie a bowline?")
async def ask_prefix(ctx: commands.Context, *, prompt: str):
    async with ctx.typing():
        answer = await llm_complete(prompt)
    for part in chunk(answer):
        await ctx.reply(part, mention_author=False)

# Quick liveness check
@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send("pong 🏓 (yarrr!)")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
