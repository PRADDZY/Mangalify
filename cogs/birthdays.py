# cogs/birthdays.py

import os
import json
import io
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils.db_manager import db_manager

STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))

class Birthdays(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    birthday_group = app_commands.Group(name="birthday", description="Manage your birthday")

    @birthday_group.command(name="set", description="Set your birthday for server announcements.")
    @app_commands.describe(
        day="Day of your birth (1-31)",
        month="Month of your birth (1-12)",
        year="Year of your birth (e.g., 2000)"
    )
    async def set_birthday(self, interaction: discord.Interaction, day: app_commands.Range[int, 1, 31], month: app_commands.Range[int, 1, 12], year: app_commands.Range[int, 1900, 2024]):
        try:
            # Validate if the date is a real calendar date
            datetime(year, month, day)
        except ValueError:
            await interaction.response.send_message("That's not a valid date. Please check the day and month.", ephemeral=True)
            return

        await db_manager.set_birthday(interaction.user.id, day, month, year)
        await interaction.response.send_message(f"Your birthday has been set to {day}/{month}/{year}.", ephemeral=True)

    @birthday_group.command(name="view", description="Check the birthday you have set.")
    async def view_birthday(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await db_manager.get_birthday(user_id)
        if data:
            await interaction.response.send_message(f"Your birthday is set to {data['day']}/{data['month']}/{data['year']}.", ephemeral=True)
        else:
            await interaction.response.send_message("You haven't set your birthday yet. Use `/birthday set`.", ephemeral=True)

    @birthday_group.command(name="remove", description="Remove your birthday from the bot.")
    async def remove_birthday(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        was_deleted = await db_manager.delete_birthday(user_id)
        if was_deleted:
            await interaction.response.send_message("Your birthday has been removed.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have a birthday set.", ephemeral=True)

    @app_commands.command(name="force_add_birthday", description="[STAFF] Add or update a birthday for a specific user.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    @app_commands.describe(
        user="The user whose birthday you want to set.",
        day="Day of birth (1-31)",
        month="Month of birth (1-12)",
        year="Year of birth (e.g., 2000)"
    )
    async def force_add_birthday(self, interaction: discord.Interaction, user: discord.Member, day: app_commands.Range[int, 1, 31], month: app_commands.Range[int, 1, 12], year: app_commands.Range[int, 1900, 2024]):
        try:
            datetime(year, month, day)
        except ValueError:
            await interaction.response.send_message(f"Invalid date provided for {user.display_name}.", ephemeral=True)
            return

        await db_manager.set_birthday(user.id, day, month, year)
        await interaction.response.send_message(f"Successfully set {user.mention}'s birthday to {day}/{month}/{year}.", ephemeral=True)

    @force_add_birthday.error
    async def on_force_add_birthday_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
            raise error

    @birthday_group.command(name="export", description="[STAFF] Export all birthdays as JSON (user_id/day/month/year).")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def export_birthdays(self, interaction: discord.Interaction):
        cursor = await db_manager.get_all_birthdays()
        data = []
        async for doc in cursor:
            data.append({
                "user_id": doc.get("_id"),
                "day": doc.get("day"),
                "month": doc.get("month"),
                "year": doc.get("year"),
            })
        payload = json.dumps(data, ensure_ascii=True, indent=2)
        file_obj = io.StringIO(payload)
        discord_file = discord.File(file_obj, filename="birthdays.json")
        await interaction.response.send_message("Exported birthdays.", file=discord_file, ephemeral=True)

    @birthday_group.command(name="import_json", description="[STAFF] Import birthdays from JSON array.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    @app_commands.describe(json_payload="JSON array of objects with user_id, day, month, year")
    async def import_birthdays(self, interaction: discord.Interaction, json_payload: str):
        try:
            items = json.loads(json_payload)
            if not isinstance(items, list):
                raise ValueError("Payload must be a JSON array")
        except Exception as exc:
            await interaction.response.send_message(f"Invalid JSON: {exc}", ephemeral=True)
            return

        imported = 0
        skipped = 0
        for item in items:
            try:
                user_id = int(item.get("user_id"))
                day = int(item.get("day"))
                month = int(item.get("month"))
                year = int(item.get("year"))
                datetime(year, month, day)  # validate date
                await db_manager.set_birthday(user_id, day, month, year)
                imported += 1
            except Exception:
                skipped += 1
                continue

        await interaction.response.send_message(
            f"Import finished. Added/updated: {imported}. Skipped: {skipped}.",
            ephemeral=True,
        )

    @birthday_group.command(name="cleanup_departed", description="[STAFF] Remove birthdays for users no longer in the server.")
    @app_commands.checks.has_role(STAFF_ROLE_ID)
    async def cleanup_departed(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Cannot run outside a guild context.", ephemeral=True)
            return

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

        await interaction.response.send_message(f"Cleanup complete. Removed {removed} departed members.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Birthdays(bot))