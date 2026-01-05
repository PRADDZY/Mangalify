# utils/api_client.py

import os
import asyncio
import logging
import aiohttp
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
        
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') if gemini_key else None
        
        self.calendarific_api_key = os.getenv("CALENDARIFIC_API_KEY")
        self.calendarific_country = os.getenv("CALENDARIFIC_COUNTRY_CODE")
        self._session = None

        self._max_retries = 3
        self._backoff_base = 0.5  # seconds

    async def _get_session(self):
        if self._session is None: self._session = aiohttp.ClientSession()
        return self._session

    async def _with_retry(self, label: str, coro_factory):
        """Retry an async operation with exponential backoff."""
        for attempt in range(1, self._max_retries + 1):
            try:
                return await coro_factory()
            except Exception as exc:
                if attempt == self._max_retries:
                    logger.error("%s failed after %s attempts: %s", label, attempt, exc, extra={"event": "retry_failed", "label": label, "attempt": attempt})
                    raise
                sleep_for = self._backoff_base * (2 ** (attempt - 1))
                logger.warning("%s attempt %s failed: %s; retrying in %.2fs", label, attempt, exc, sleep_for, extra={"event": "retry_wait", "label": label, "attempt": attempt, "sleep": sleep_for})
                await asyncio.sleep(sleep_for)

    async def get_holidays(self, year: int, month: int):
        if not self.calendarific_api_key:
            return None
        url = (
            f"https://calendarific.com/api/v2/holidays?"
            f"&api_key={self.calendarific_api_key}&country={self.calendarific_country}"
            f"&year={year}&month={month}"
        )
        try:
            session = await self._get_session()

            async def _fetch():
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Calendarific status {response.status}")
                    data = await response.json()
                    return data.get("response", {}).get("holidays", [])

            return await self._with_retry("Calendarific fetch", _fetch)
        except Exception as e:
            logger.error("Exception while fetching holidays: %s", e, extra={"event": "calendarific_error", "year": year, "month": month})
            return None

    async def generate_wish_text(self, holiday_name: str):
        if not self.gemini_model: return None
            
        # FIX: New prompt for rich markdown text
        prompt = (
            f"Create a wish message for the festival of {holiday_name} for a Discord server. "
            "The message must be formatted using Discord's markdown. "
            "Start with a bold header using a hash symbol (e.g., '# Happy {holiday_name}!'). "
            "Include bold (`**text**`), italics (`*text*`), and a block quote (`> quote`). "
            "Do not use embeds. The output should be a raw text message."
        )

        try:
            async def _gen():
                response = await self.gemini_model.generate_content_async(prompt)
                return response.text.strip() if response.parts else None

            return await self._with_retry("Gemini holiday wish", _gen)
        except Exception as e:
            logger.error("Gemini API error for holiday wish: %s", e, extra={"event": "gemini_holiday_error", "holiday": holiday_name})
            return f"Happy {holiday_name}! Wishing everyone a wonderful celebration."

    async def generate_birthday_wish_text(self, member_name: str, member_mention: str):
        if not self.gemini_model: return None
            
        # FIX: New prompt for rich markdown text, including the user's mention
        prompt = (
            f"Create a personal and cheerful birthday wish for a Discord community member named {member_name}. "
            "The message must be formatted using Discord's markdown. "
            f"Start the message with a header like '# Happy Birthday, {member_name}! 🎉'. "
            f"Make sure to include their mention, which is `{member_mention}`, in the body of the message. "
            "Use other formatting like bold, italics, and block quotes to make it feel special. "
            "Encourage others to wish them a happy birthday. Do not use embeds."
        )

        try:
            async def _gen():
                response = await self.gemini_model.generate_content_async(prompt)
                return response.text.strip() if response.parts else None

            text = await self._with_retry("Gemini birthday wish", _gen)
            if text:
                return text
        except Exception as e:
            logger.error("Gemini API error for birthday wish: %s", e, extra={"event": "gemini_birthday_error", "member": member_name})
        return f"# 🎉 Happy Birthday, {member_name}! 🎉\n\n> Hope you have a fantastic day filled with joy and laughter!\n\nEveryone, please wish a happy birthday to {member_mention}!"

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()

api_client = ApiClient()