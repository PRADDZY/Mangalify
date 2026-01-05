# cogs/wishes.py

import os
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from datetime import datetime, time
import pytz

from utils.db_manager import db_manager
from utils.api_client import api_client

# Simple helper to avoid repeating message send error handling
async def _safe_send(channel: discord.abc.Messageable | None, content: str):
    if not channel:
        return
    try:
        await channel.send(content)
    except Exception as exc:
        print(f"⚠️ Failed to send message to channel {getattr(channel, 'id', 'unknown')}: {exc}")

GUILD_ID = int(os.getenv("GUILD_ID"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))
BIRTHDAY_ROLE_ID = int(os.getenv("BIRTHDAY_ROLE_ID"))
WISHES_CHANNEL_ID = int(os.getenv("WISHES_CHANNEL_ID"))
BIRTHDAY_CHANNEL_ID = int(os.getenv("BIRTHDAY_CHANNEL_ID"))
STAFF_ALERTS_CHANNEL_ID = int(os.getenv("STAFF_ALERTS_CHANNEL_ID"))
POST_TIME_UTC_STR = os.getenv("POST_TIME_UTC", "00:01")
SERVER_TIMEZONE_STR = os.getenv("SERVER_TIMEZONE", "UTC")

try:
    utc_time_parts = list(map(int, POST_TIME_UTC_STR.split(':')))
    POST_TIME = time(hour=utc_time_parts[0], minute=utc_time_parts[1], tzinfo=pytz.utc)
    SERVER_TIMEZONE = pytz.timezone(SERVER_TIMEZONE_STR)
except (ValueError, pytz.UnknownTimeZoneError):
    POST_TIME = time(hour=0, minute=1, tzinfo=pytz.utc)
    SERVER_TIMEZONE = pytz.utc

# WishModal is for staff input, it doesn't send messages, so no changes needed.
class WishModal(ui.Modal, title='Add a Custom Wish'):
    # ... (no changes here)
    name = ui.TextInput(label='Wish Name (for reference)')
    date = ui.TextInput(label='Date (DD-MM-YYYY)')
    message = ui.TextInput(label='Wish Message', style=discord.TextStyle.paragraph)
    role_to_ping = ui.TextInput(label='Role ID to Ping (optional)', required=False)
    async def on_submit(self, interaction: discord.Interaction):
        # ... (no changes here)
        try:
            wish_date = datetime.strptime(self.date.value, "%d-%m-%Y")
        except ValueError:
            await interaction.response.send_message("Invalid date format.", ephemeral=True)
            return
        role_id = None
        if self.role_to_ping.value.lower() == 'everyone': role_id = 'everyone'
        elif self.role_to_ping.value.isdigit(): role_id = int(self.role_to_ping.value)
        await db_manager.add_manual_wish(
            name=self.name.value, day=wish_date.day, month=wish_date.month, year=wish_date.year,
            message=self.message.value, role_id=role_id
        )
        await interaction.response.send_message(f"Custom wish '{self.name.value}' saved.", ephemeral=True)

class Wishes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=POST_TIME)
    async def daily_task(self):
        today = datetime.now(SERVER_TIMEZONE)
        print(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Running daily task...")
        try:
            await self._cleanup_birthday_roles(today)
            await self._check_for_birthdays(today)
            await self._check_for_holidays(today)
        except Exception as exc:
            await _safe_send(self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID), f"❌ Daily task failed: {exc}")
            print(f"❌ Daily task encountered an error: {exc}")

    @daily_task.before_loop
    async def before_daily_task(self):
        await self.bot.wait_until_ready()

    async def _check_for_holidays(self, today: datetime):
        alerts_channel = self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID)
        if not alerts_channel:
            print("⚠️ STAFF_ALERTS_CHANNEL_ID is not configured or not found.")
        holidays = await api_client.get_holidays(today.year, today.month)
        if holidays is None:
            if alerts_channel: await alerts_channel.send("⚠️ **API Error:** Could not fetch holidays.")
            return

        todays_holidays_names = [h['name'] for h in holidays if h['date']['iso'] == today.strftime('%Y-%m-%d')]
        if todays_holidays_names:
            holiday_list_str = ", ".join(f"**{name}**" for name in todays_holidays_names)
            log_message = f"ℹ️ **Daily Check:** Found {len(todays_holidays_names)} holiday(s): {holiday_list_str}."
            if alerts_channel: await alerts_channel.send(log_message)

        for holiday_name in todays_holidays_names:
            wish_text = await api_client.generate_wish_text(holiday_name)
            wishes_channel = self.bot.get_channel(WISHES_CHANNEL_ID)
            
            # FIX: Send raw markdown text instead of an embed
            if wish_text:
                await _safe_send(wishes_channel, wish_text)
            elif alerts_channel:
                await alerts_channel.send(f"⚠️ **API Error:** Failed to generate wish text for **{holiday_name}**.")

    async def _check_for_birthdays(self, today: datetime):
        guild = self.bot.get_guild(GUILD_ID)
        birthday_channel = self.bot.get_channel(BIRTHDAY_CHANNEL_ID)
        birthday_role = guild.get_role(BIRTHDAY_ROLE_ID) if guild else None
        if not all([guild, birthday_channel, birthday_role]):
            await _safe_send(self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID), "⚠️ Birthday check skipped: guild/channel/role missing.")
            return

        cursor = db_manager.get_birthdays_for_date(today.day, today.month)
        async for birthday_data in cursor:
            member = guild.get_member(birthday_data['_id'])
            if member:
                try:
                    birthday_message = await api_client.generate_birthday_wish_text(member.display_name, member.mention)
                    
                    await member.add_roles(birthday_role, reason="Birthday")
                    
                    # FIX: Send raw markdown text instead of an embed
                    if birthday_message:
                        await _safe_send(birthday_channel, birthday_message)
                    
                    await db_manager.add_user_to_role_log(birthday_data['_id'], today.strftime('%Y-%m-%d'))
                except Exception as e:
                    print(f"❌ UNEXPECTED ERROR during birthday announcement for {member.display_name}: {e}")

    async def _cleanup_birthday_roles(self, today: datetime):
        # ... (no changes here)
        guild = self.bot.get_guild(GUILD_ID)
        birthday_role = guild.get_role(BIRTHDAY_ROLE_ID) if guild else None
        if not guild or not birthday_role: return
        cursor = await db_manager.get_users_with_birthday_role()
        async for user_log in cursor:
            if user_log.get('date_added') != today.strftime('%Y-%m-%d'):
                member = guild.get_member(user_log['_id'])
                if member and birthday_role in member.roles:
                    await member.remove_roles(birthday_role, reason="Birthday ended")
                await db_manager.remove_user_from_role_log(user_log['_id'])

    # ... (no changes to Staff Commands)
    @app_commands.command(name="add_wish", description="[STAFF] Add a custom wish for a specific date.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def add_wish(self, interaction: discord.Interaction):
        await interaction.response.send_modal(WishModal())

    @app_commands.command(name="status", description="[STAFF] Check the operational status of the bot.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def status(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Bot is online. Latency: {latency}ms.", ephemeral=True)
    
    @add_wish.error
    @status.error
    async def on_staff_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # ... (no changes here)
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            raise error

async def setup(bot: commands.Bot):
    cog = Wishes(bot)
    await bot.add_cog(cog)