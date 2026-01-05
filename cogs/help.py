import discord
from discord import app_commands
from discord.ext import commands


HELP_TEXT = (
    "**Available Commands**\n"
    "• /birthday set <day> <month> <year> — Set your birthday\n"
    "• /birthday view — View your birthday\n"
    "• /birthday remove — Remove your birthday\n"
    "• /birthday export — [Staff] Export birthdays\n"
    "• /birthday import_json — [Staff] Import birthdays\n"
    "• /birthday cleanup_departed — [Staff] Cleanup departed members\n"
    "• /add_wish — [Staff] Add a custom wish (modal)\n"
    "• /status — [Staff] Bot status and scheduler times"
)

ABOUT_TEXT = (
    "**Mangalify** — Discord bot for birthdays and festivals.\n"
    "Automates birthday wishes, festival greetings, role assignment, and staff alerts."
)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show bot commands and quick usage.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(HELP_TEXT, ephemeral=True)

    @app_commands.command(name="about", description="Learn about this bot.")
    async def about(self, interaction: discord.Interaction):
        await interaction.response.send_message(ABOUT_TEXT, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
