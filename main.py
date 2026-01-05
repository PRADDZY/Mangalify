# main.py

import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = None  # Populated after validation
GUILD_ID = None   # Populated after validation


def _require_env(name: str, cast=str):
    """Fetch and cast an environment variable, failing fast with a clear message."""
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        raise SystemExit(f"Missing required environment variable: {name}")
    try:
        return cast(raw_value)
    except Exception:
        raise SystemExit(f"Invalid value for {name}: expected {cast.__name__}")


def _validate_post_time():
    value = os.getenv("POST_TIME_UTC", "00:01")
    parts = value.split(":")
    if len(parts) != 2:
        raise SystemExit("POST_TIME_UTC must be in HH:MM format (e.g., 00:01)")
    hour, minute = parts
    if not (hour.isdigit() and minute.isdigit()):
        raise SystemExit("POST_TIME_UTC must contain only digits (HH:MM)")
    hour_i, minute_i = int(hour), int(minute)
    if not (0 <= hour_i <= 23 and 0 <= minute_i <= 59):
        raise SystemExit("POST_TIME_UTC must be a valid 24h time (00:00-23:59)")


def validate_environment():
    """Fail fast if required configuration is missing or malformed."""
    global BOT_TOKEN, GUILD_ID

    BOT_TOKEN = _require_env("BOT_TOKEN", str)
    GUILD_ID = _require_env("GUILD_ID", int)

    # Validate other required IDs early so cogs don't fail at import time
    required_ints = [
        "STAFF_ROLE_ID",
        "BIRTHDAY_ROLE_ID",
        "WISHES_CHANNEL_ID",
        "BIRTHDAY_CHANNEL_ID",
        "STAFF_ALERTS_CHANNEL_ID",
    ]
    for name in required_ints:
        _require_env(name, int)

    _validate_post_time()

class WishesBot(commands.Bot):
    def __init__(self):
        # Define necessary intents
        intents = discord.Intents.default()
        intents.members = True # Required for role management
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This is the recommended way to load cogs
        print("Loading cogs...")
        for filename in os.listdir('./cogs'):
            # Ignore files like __init__.py and folders like __pycache__
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Loaded cog: {filename}")
                except Exception as e:
                    print(f"Failed to load cog {filename}: {e}")
        
        # Sync slash commands with the specified guild
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced.")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

async def main():
    validate_environment()
    bot = WishesBot()
    async with bot:
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())