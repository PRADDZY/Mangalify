# test.py (End-to-End Functional Test - Final Corrected Version)

import sys
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from unittest.mock import patch, AsyncMock

# --- Setup Project Path ---
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# --- Load Config and Bot Modules ---
load_dotenv()
from utils.db_manager import db_manager
from cogs.wishes import Wishes

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WISHES_CHANNEL_ID = int(os.getenv("WISHES_CHANNEL_ID"))
BIRTHDAY_CHANNEL_ID = int(os.getenv("BIRTHDAY_CHANNEL_ID"))
STAFF_ALERTS_CHANNEL_ID = int(os.getenv("STAFF_ALERTS_CHANNEL_ID"))
MOCK_HOLIDAY = "Bot Markdown Test Day"

class E2ETestRunner(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report = []

    # FIX: All logic is moved back into on_ready, which runs AFTER the bot's cache is ready.
    # The faulty setup_hook has been removed.
    async def on_ready(self):
        print(f"Logged in as {self.user} to run E2E tests.")
        await self.wait_until_ready() # Explicitly wait for the cache to be fully populated

        guild = self.get_guild(GUILD_ID)
        if not guild:
            print(f"❌ FATAL: Bot could not find the specified Guild (ID: {GUILD_ID}). Aborting.")
            await self.close()
            return

        wishes_channel = guild.get_channel(WISHES_CHANNEL_ID)
        birthday_channel = guild.get_channel(BIRTHDAY_CHANNEL_ID)
        alerts_channel = guild.get_channel(STAFF_ALERTS_CHANNEL_ID)

        if not all([wishes_channel, birthday_channel, alerts_channel]):
             print("❌ FATAL: Could not find one or more required channels. Please check all Channel IDs in .env. Aborting.")
             await self.close()
             return

        await wishes_channel.send(f"🚀 **Starting E2E Markdown Test at {datetime.now():%H:%M:%S}**")

        await self.test_birthday_announcement(guild, birthday_channel)
        await self.test_holiday_announcement(guild, wishes_channel)
        
        await self.send_report(alerts_channel)
        await self.close()

    async def test_birthday_announcement(self, guild, birthday_channel):
        print("▶️ Running: Birthday Announcement Test")
        today = datetime.now()
        tester_bot_id = self.user.id
        tester_bot_mention = self.user.mention

        await db_manager.set_birthday(tester_bot_id, today.day, today.month, 2020)
        
        def is_birthday_message(message):
            return message.channel.id == birthday_channel.id and tester_bot_mention in message.content

        try:
            wishes_cog = Wishes(self)
            _, message = await asyncio.gather(
                wishes_cog._check_for_birthdays(today),
                self.wait_for('message', check=is_birthday_message, timeout=15.0)
            )
            self.report.append(f"✅ **Birthday Test:** Bot successfully posted the birthday markdown message.")
        except asyncio.TimeoutError:
            self.report.append("❌ **Birthday Test:** Bot FAILED to post the birthday message.")
        finally:
            await db_manager.delete_birthday(tester_bot_id)

    async def test_holiday_announcement(self, guild, wishes_channel):
        print("▶️ Running: Holiday Announcement Test")
        today = datetime.now()
        
        def is_holiday_message(message):
            return message.channel.id == wishes_channel.id and MOCK_HOLIDAY in message.content

        mock_api_response = [{'name': MOCK_HOLIDAY, 'date': {'iso': today.strftime('%Y-%m-%d')}}]
        
        with patch('cogs.wishes.api_client.get_holidays', new_callable=AsyncMock, return_value=mock_api_response):
            try:
                wishes_cog = Wishes(self)
                _, message = await asyncio.gather(
                    wishes_cog._check_for_holidays(today),
                    self.wait_for('message', check=is_holiday_message, timeout=25.0)
                )
                self.report.append(f"✅ **Holiday Test:** Bot successfully posted the holiday markdown message.")
            except asyncio.TimeoutError:
                self.report.append("❌ **Holiday Test:** Bot FAILED to post the holiday message.")

    async def send_report(self, alerts_channel):
        print("--- Test Suite Finished. Sending Report. ---")
        is_failure = any("❌" in s for s in self.report)
        
        report_title = "## E2E Markdown Test Report"
        status_icon = "❌" if is_failure else "✅"
        report_body = "\n".join([f"- {line}" for line in self.report]) or "- No tests were run."
        
        final_message = f"{status_icon} {report_title}\n{report_body}"
        
        try:
            if alerts_channel:
                await alerts_channel.send(final_message)
        except Exception as e:
            print(f"FATAL: Could not send the report. Error: {e}")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.members = True
    intents.message_content = True
    
    runner = E2ETestRunner(command_prefix="!test!", intents=intents)
    runner.run(BOT_TOKEN)