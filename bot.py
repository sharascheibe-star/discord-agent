import os
import discord
from discord.ext import commands

# Load the Discord bot token from an environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

# Set up bot permissions and prefix
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read messages

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")

# Run the bot
bot.run(TOKEN)
