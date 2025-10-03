import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
    
    # Holiday API
    HOLIDAY_API_KEY = os.getenv("HOLIDAY_API_KEY")
    COUNTRY_CODE = os.getenv("COUNTRY_CODE", "IN")
    YEAR = int(os.getenv("YEAR", "2025"))
    
    # Hugging Face
    HF_API_KEY = os.getenv("HF_API_KEY")
    HF_MODEL = os.getenv("HF_MODEL", "bigscience/bloomz-560m")
    
    # Bot Settings
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
    FESTIVAL_CHANNEL_ID = int(os.getenv("FESTIVAL_CHANNEL_ID", "0"))
    DAILY_REMINDER_TIME = os.getenv("DAILY_REMINDER_TIME", "22:00")  # IST
    ENABLE_DAILY_REMINDER = os.getenv("ENABLE_DAILY_REMINDER", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def validate():
        """Validate required configs are set"""
        missing = []
        if not Config.DISCORD_TOKEN:
            missing.append("DISCORD_TOKEN")
        if not Config.HOLIDAY_API_KEY:
            missing.append("HOLIDAY_API_KEY")
        if not Config.HF_API_KEY:
            missing.append("HF_API_KEY")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Run validation at import
Config.validate()
