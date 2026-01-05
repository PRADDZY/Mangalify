# cogs/wishes.py

import os
import re
import logging
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import pytz

from utils.db_manager import db_manager
from utils.api_client import api_client

logger = logging.getLogger(__name__)

# Simple helper to avoid repeating message send error handling
async def _safe_send(channel: discord.abc.Messageable | None, content: str):
    if not channel:
        return
    try:
        await channel.send(content)
    except Exception as exc:
        logger.warning("Failed to send message to channel %s: %s", getattr(channel, 'id', 'unknown'), exc)

GUILD_ID = int(os.getenv("GUILD_ID"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))
BIRTHDAY_ROLE_ID = int(os.getenv("BIRTHDAY_ROLE_ID"))
WISHES_CHANNEL_ID = int(os.getenv("WISHES_CHANNEL_ID"))
BIRTHDAY_CHANNEL_ID = int(os.getenv("BIRTHDAY_CHANNEL_ID"))
STAFF_ALERTS_CHANNEL_ID = int(os.getenv("STAFF_ALERTS_CHANNEL_ID"))
POST_TIME_UTC_STR = os.getenv("POST_TIME_UTC", "00:01")
SERVER_TIMEZONE_STR = os.getenv("SERVER_TIMEZONE", "UTC")
HOLIDAY_APPROVAL_MODE = os.getenv("HOLIDAY_APPROVAL_MODE", "false").lower() == "true"

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
    _daily_started = False  # class-level guard to avoid duplicate loop starts
    _indexes_ready = False

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not Wishes._daily_started:
            Wishes._daily_started = True
            self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=POST_TIME)
    async def daily_task(self):
        today = datetime.now(SERVER_TIMEZONE)
        logger.info(
            "Running daily task",
            extra={"event": "daily_task_start", "ts_local": today.strftime('%Y-%m-%d %H:%M:%S'), "tz": SERVER_TIMEZONE_STR},
        )
        alerts_channel = self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID)
        try:
            removed_roles = await self._cleanup_birthday_roles(today)
            removed_departed = await self._cleanup_departed_members()
            birthday_count = await self._check_for_birthdays(today)
            holiday_count = await self._check_for_holidays(today)
            summary = (
                f"✅ Daily task done | Birthdays: {birthday_count} | Holidays: {holiday_count} | Roles removed: {removed_roles} | "
                f"Departed cleaned: {removed_departed} | "
                f"Next run: {self._next_run_time_str()} ({SERVER_TIMEZONE_STR})"
            )
            await _safe_send(alerts_channel, summary)
            await self._store_scheduler_meta(next_run=self._next_run_time_iso(), last_run=today.astimezone(SERVER_TIMEZONE).isoformat())
            logger.info(
                "Daily task completed",
                extra={
                    "event": "daily_task_done",
                    "birthdays": birthday_count,
                    "holidays": holiday_count,
                    "roles_removed": removed_roles,
                    "departed_removed": removed_departed,
                    "next_run": self._next_run_time_iso(),
                    "tz": SERVER_TIMEZONE_STR,
                },
            )
        except Exception as exc:
            await _safe_send(self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID), f"❌ Daily task failed: {exc}")
            logger.exception("Daily task encountered an error", extra={"event": "daily_task_error", "error": str(exc)})

    @daily_task.before_loop
    async def before_daily_task(self):
        await self.bot.wait_until_ready()
        if not Wishes._indexes_ready:
            try:
                await db_manager.ensure_indexes()
                Wishes._indexes_ready = True
            except Exception as exc:
                logger.warning("Failed to ensure indexes", extra={"event": "ensure_indexes_error", "error": str(exc)})
        alerts_channel = self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID)
        last_meta = await self._get_scheduler_meta()
        last_run = last_meta.get("last_run_at") if last_meta else "unknown"
        next_run = self._next_run_time_str()
        await _safe_send(alerts_channel, f"ℹ️ Daily task scheduled. Next run: {next_run} ({SERVER_TIMEZONE_STR}) | Last run: {last_run}")

    async def _check_for_holidays(self, today: datetime):
        alerts_channel = self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID)
        if not alerts_channel:
            logger.warning("STAFF_ALERTS_CHANNEL_ID is not configured or not found.", extra={"event": "alerts_channel_missing"})
        holidays = await api_client.get_holidays(today.year, today.month)
        if holidays is None:
            if alerts_channel: await alerts_channel.send("⚠️ **API Error:** Could not fetch holidays (Calendarific unreachable or misconfigured).")
            logger.warning("Holiday fetch returned None", extra={"event": "holidays_none", "year": today.year, "month": today.month})
            return 0

        todays_holidays_names = [h['name'] for h in holidays if h['date']['iso'] == today.strftime('%Y-%m-%d')]
        if todays_holidays_names:
            holiday_list_str = ", ".join(f"**{name}**" for name in todays_holidays_names)
            log_message = f"ℹ️ **Daily Check:** Found {len(todays_holidays_names)} holiday(s): {holiday_list_str}."
            if alerts_channel: await alerts_channel.send(log_message)

        sent = 0
        for holiday_name in todays_holidays_names:
            wish_text = await api_client.generate_wish_text(holiday_name)
            wishes_channel = self.bot.get_channel(WISHES_CHANNEL_ID)
            
            # FIX: Send raw markdown text instead of an embed
            if wish_text:
                safe_text = self._guard_message(wish_text, kind="holiday", name=holiday_name)
                if HOLIDAY_APPROVAL_MODE:
                    preview = (
                        f"🔎 Holiday preview for **{holiday_name}** (approval required).\n"
                        f"Use `/holiday_post holiday_name:<name> content:<text>` to post.\n\n{safe_text}"
                    )
                    await _safe_send(alerts_channel, preview)
                else:
                    await _safe_send(wishes_channel, safe_text)
                    sent += 1
            elif alerts_channel:
                await alerts_channel.send(f"⚠️ **API Error:** Failed to generate wish text for **{holiday_name}**.")

        return sent

    async def _check_for_birthdays(self, today: datetime):
        guild = self.bot.get_guild(GUILD_ID)
        birthday_channel = self.bot.get_channel(BIRTHDAY_CHANNEL_ID)
        birthday_role = guild.get_role(BIRTHDAY_ROLE_ID) if guild else None
        if not all([guild, birthday_channel, birthday_role]):
            await _safe_send(self.bot.get_channel(STAFF_ALERTS_CHANNEL_ID), "⚠️ Birthday check skipped: guild/channel/role missing.")
            logger.warning("Birthday check skipped: missing guild/channel/role", extra={"event": "birthday_skip"})
            return 0

        cursor = db_manager.get_birthdays_for_date(today.day, today.month)
        sent = 0
        async for birthday_data in cursor:
            member = guild.get_member(birthday_data['_id'])
            if member:
                try:
                    birthday_message = await api_client.generate_birthday_wish_text(member.display_name, member.mention)
                    
                    await member.add_roles(birthday_role, reason="Birthday")
                    
                    # FIX: Send raw markdown text instead of an embed
                    if birthday_message:
                        safe_text = self._guard_message(birthday_message, kind="birthday", name=member.display_name)
                        await _safe_send(birthday_channel, safe_text)
                        sent += 1
                    
                    await db_manager.add_user_to_role_log(birthday_data['_id'], today.strftime('%Y-%m-%d'))
                except Exception as e:
                    logger.exception("Unexpected error during birthday announcement", extra={"event": "birthday_error", "member": member.display_name, "error": str(e)})
        return sent

    async def _cleanup_birthday_roles(self, today: datetime):
        # ... (no changes here)
        guild = self.bot.get_guild(GUILD_ID)
        birthday_role = guild.get_role(BIRTHDAY_ROLE_ID) if guild else None
        if not guild or not birthday_role: return
        cursor = await db_manager.get_users_with_birthday_role()
        removed = 0
        async for user_log in cursor:
            if user_log.get('date_added') != today.strftime('%Y-%m-%d'):
                member = guild.get_member(user_log['_id'])
                if member and birthday_role in member.roles:
                    await member.remove_roles(birthday_role, reason="Birthday ended")
                    removed += 1
                await db_manager.remove_user_from_role_log(user_log['_id'])
        return removed

    def _guard_message(self, text: str, kind: str, name: str) -> str:
        """Apply basic safety filters and length cap."""
        if not text:
            return ""
        bad_words = ["fuck", "shit", "bitch", "bastard", "damn"]
        sanitized = text
        for bad in bad_words:
            sanitized = re.sub(bad, "***", sanitized, flags=re.IGNORECASE)
        max_len = 900
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len] + "..."
        return sanitized

    async def _cleanup_departed_members(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return 0
        removed = 0
        cursor = await db_manager.get_all_birthdays()
        async for entry in cursor:
            user_id = entry.get("_id")
            if not user_id:
                continue
            member = guild.get_member(user_id)
            if member is None:
                await db_manager.delete_birthday(user_id)
                await db_manager.remove_user_from_role_log(user_id)
                removed += 1
        return removed

    def _next_run_time_str(self) -> str:
        """Compute next run time for the daily task in server timezone."""
        now = datetime.now(SERVER_TIMEZONE)
        target = now.replace(hour=POST_TIME.hour, minute=POST_TIME.minute, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        return target.strftime('%Y-%m-%d %H:%M')

    def _next_run_time_iso(self) -> str:
        now = datetime.now(SERVER_TIMEZONE)
        target = now.replace(hour=POST_TIME.hour, minute=POST_TIME.minute, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        return target.isoformat()

    async def _store_scheduler_meta(self, next_run: str | None, last_run: str | None):
        try:
            await db_manager.upsert_scheduler_meta("daily_task", next_run_at=next_run, last_run_at=last_run)
        except Exception as exc:
            logger.warning("Failed to store scheduler meta", extra={"event": "scheduler_meta_store_error", "error": str(exc)})

    async def _get_scheduler_meta(self):
        try:
            return await db_manager.get_scheduler_meta("daily_task")
        except Exception as exc:
            logger.warning("Failed to load scheduler meta", extra={"event": "scheduler_meta_load_error", "error": str(exc)})
            return None

    # ... (no changes to Staff Commands)
    @app_commands.command(name="add_wish", description="[STAFF] Add a custom wish for a specific date.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def add_wish(self, interaction: discord.Interaction):
        await interaction.response.send_modal(WishModal())

    @app_commands.command(name="status", description="[STAFF] Check the operational status of the bot.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def status(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        meta = await self._get_scheduler_meta()
        last_run = meta.get("last_run_at") if meta else "unknown"
        next_run = meta.get("next_run_at") if meta else "unknown"
        await interaction.response.send_message(
            f"Bot is online. Latency: {latency}ms.\n"
            f"Daily task — Last run: {last_run}, Next run: {next_run}",
            ephemeral=True,
        )

    @app_commands.command(name="holiday_post", description="[STAFF] Post an approved holiday wish to the channel.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    @app_commands.describe(holiday_name="Name of the holiday", content="Message to post")
    async def holiday_post(self, interaction: discord.Interaction, holiday_name: str, content: str):
        wishes_channel = self.bot.get_channel(WISHES_CHANNEL_ID)
        if not wishes_channel:
            await interaction.response.send_message("Wishes channel not configured.", ephemeral=True)
            return
        safe_text = self._guard_message(content, kind="holiday_manual", name=holiday_name)
        await wishes_channel.send(safe_text)
        await interaction.response.send_message(f"Posted holiday wish for {holiday_name}.", ephemeral=True)
    
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