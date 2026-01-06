import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def mock_env(monkeypatch):
    """Set up minimal environment for tests."""
    monkeypatch.setenv("LOAD_DOTENV", "false")
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("GUILD_ID", "123")
    monkeypatch.setenv("STAFF_ROLE_ID", "456")
    monkeypatch.setenv("BIRTHDAY_ROLE_ID", "789")
    monkeypatch.setenv("WISHES_CHANNEL_ID", "111")
    monkeypatch.setenv("BIRTHDAY_CHANNEL_ID", "222")
    monkeypatch.setenv("STAFF_ALERTS_CHANNEL_ID", "333")
    monkeypatch.setenv("POST_TIME_UTC", "00:01")
    monkeypatch.setenv("SERVER_TIMEZONE", "UTC")
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")


@pytest.mark.asyncio
async def test_holiday_check_with_holidays(mock_env):
    """Test that holidays are detected and wishes are generated."""
    from cogs.wishes import Wishes
    from unittest.mock import AsyncMock

    # Mock bot and channels
    mock_bot = MagicMock()
    mock_wishes_channel = AsyncMock()
    mock_alerts_channel = AsyncMock()
    mock_bot.get_channel.side_effect = lambda cid: {
        111: mock_wishes_channel,
        333: mock_alerts_channel,
    }.get(cid)

    # Prevent daily task from starting
    with patch.object(Wishes, '_daily_started', True):
        # Create cog instance
        cog = Wishes(mock_bot)

    # Mock API client
    with patch("cogs.wishes.api_client") as mock_api:
        mock_api.get_holidays = AsyncMock(return_value=[
            {"name": "Test Day", "date": {"iso": "2026-01-06"}},
        ])
        mock_api.generate_wish_text = AsyncMock(return_value="Happy Test Day!")

        today = datetime(2026, 1, 6)
        count = await cog._check_for_holidays(today)

        assert count == 1
        assert mock_api.get_holidays.called
        assert mock_api.generate_wish_text.called


@pytest.mark.asyncio
async def test_holiday_check_no_holidays(mock_env):
    """Test holiday check when no holidays found."""
    from cogs.wishes import Wishes

    mock_bot = MagicMock()
    mock_alerts_channel = MagicMock()
    mock_bot.get_channel.return_value = mock_alerts_channel

    with patch.object(Wishes, '_daily_started', True):
        cog = Wishes(mock_bot)

    with patch("cogs.wishes.api_client") as mock_api:
        mock_api.get_holidays = AsyncMock(return_value=[])

        today = datetime(2026, 1, 6)
        count = await cog._check_for_holidays(today)

        assert count == 0


@pytest.mark.asyncio
async def test_birthday_check_with_birthdays(mock_env):
    """Test birthday check finds and announces birthdays."""
    from cogs.wishes import Wishes

    mock_bot = MagicMock()
    mock_guild = MagicMock()
    mock_birthday_channel = AsyncMock()
    mock_role = MagicMock()
    mock_member = AsyncMock()
    mock_member.display_name = "TestUser"
    mock_member.mention = "<@12345>"
    mock_member.add_roles = AsyncMock()

    mock_bot.get_guild.return_value = mock_guild
    mock_bot.get_channel.return_value = mock_birthday_channel
    mock_guild.get_role.return_value = mock_role
    mock_guild.get_member.return_value = mock_member

    with patch.object(Wishes, '_daily_started', True):
        cog = Wishes(mock_bot)

    # Mock db cursor as an async iterable
    class MockCursor:
        def __init__(self):
            self.items = [{"_id": 12345, "day": 6, "month": 1, "year": 2000}]
            self.index = 0
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if self.index >= len(self.items):
                raise StopAsyncIteration
            item = self.items[self.index]
            self.index += 1
            return item

    with patch("cogs.wishes.db_manager") as mock_db:
        mock_db.get_birthdays_for_date = MagicMock(return_value=MockCursor())
        mock_db.add_user_to_role_log = AsyncMock()

        with patch("cogs.wishes.api_client") as mock_api:
            mock_api.generate_birthday_wish_text = AsyncMock(return_value="Happy Birthday TestUser!")

            today = datetime(2026, 1, 6)
            count = await cog._check_for_birthdays(today)

            assert count == 1
            assert mock_member.add_roles.called
            assert mock_db.add_user_to_role_log.called


@pytest.mark.asyncio
async def test_message_guard_profanity_filter(mock_env):
    """Test that message guard filters profanity."""
    from cogs.wishes import Wishes

    mock_bot = MagicMock()
    with patch.object(Wishes, '_daily_started', True):
        cog = Wishes(mock_bot)

    dirty = "This is a fuck test with shit words"
    clean = cog._guard_message(dirty, kind="test", name="test")

    assert "fuck" not in clean.lower()
    assert "shit" not in clean.lower()
    assert "***" in clean


@pytest.mark.asyncio
async def test_message_guard_length_cap(mock_env):
    """Test that message guard caps message length."""
    from cogs.wishes import Wishes

    mock_bot = MagicMock()
    with patch.object(Wishes, '_daily_started', True):
        cog = Wishes(mock_bot)

    long_text = "A" * 1000
    capped = cog._guard_message(long_text, kind="test", name="test")

    assert len(capped) <= 903  # 900 + "..."
    assert capped.endswith("...")


@pytest.mark.asyncio
async def test_departed_member_cleanup(mock_env):
    """Test cleanup of departed members."""
    from cogs.wishes import Wishes

    mock_bot = MagicMock()
    mock_guild = MagicMock()
    mock_bot.get_guild.return_value = mock_guild
    mock_guild.get_member.return_value = None  # Member no longer in guild

    with patch.object(Wishes, '_daily_started', True):
        cog = Wishes(mock_bot)

    # Mock db cursor as an async iterable
    class MockCursor:
        def __init__(self):
            self.items = [{"_id": 99999, "day": 1, "month": 1, "year": 2000}]
            self.index = 0
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if self.index >= len(self.items):
                raise StopAsyncIteration
            item = self.items[self.index]
            self.index += 1
            return item

    with patch("cogs.wishes.db_manager") as mock_db:
        mock_db.get_all_birthdays = AsyncMock(return_value=MockCursor())
        mock_db.delete_birthday = AsyncMock()
        mock_db.remove_user_from_role_log = AsyncMock()

        removed = await cog._cleanup_departed_members()

        assert removed == 1
        assert mock_db.delete_birthday.called
        assert mock_db.remove_user_from_role_log.called
