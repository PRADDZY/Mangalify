# cogs/birthdays.py

import os
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Birthdays(bot))