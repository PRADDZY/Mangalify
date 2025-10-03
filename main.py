# main.py

import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Load essential variables from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

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
    bot = WishesBot()
    async with bot:
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())