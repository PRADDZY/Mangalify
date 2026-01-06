import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def mock_env(monkeypatch):
    """Set up minimal environment for tests."""
    monkeypatch.setenv("LOAD_DOTENV", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("CALENDARIFIC_API_KEY", "test_key")
    monkeypatch.setenv("CALENDARIFIC_COUNTRY_CODE", "US")


@pytest.mark.asyncio
async def test_get_holidays_retry_on_failure(mock_env):
    """Test that get_holidays retries on failure."""
    from utils.api_client import ApiClient
    
    client = ApiClient()
    
    with patch.object(client, "_get_session") as mock_session:
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__.return_value = None
        
        mock_session.return_value.get.return_value = mock_resp
        
        result = await client.get_holidays(2026, 1)
        
        # Should return None after retries exhausted
        assert result is None


@pytest.mark.asyncio
async def test_get_holidays_success(mock_env):
    """Test successful holiday fetch."""
    from utils.api_client import ApiClient
    
    client = ApiClient()
    
    with patch.object(client, "_get_session") as mock_session:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={
            "response": {
                "holidays": [{"name": "New Year", "date": {"iso": "2026-01-01"}}]
            }
        })
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_get = AsyncMock(return_value=mock_resp)
        mock_get.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get.__aexit__ = AsyncMock(return_value=None)
        
        mock_session.return_value.get.return_value = mock_get
    """Test fallback message when Gemini fails."""
    from utils.api_client import ApiClient
    
    client = ApiClient()
    
    # Mock the model to raise exception
    if client.gemini_model:
        with patch.object(client.gemini_model, "generate_content_async", side_effect=Exception("API Error")):
            result = await client.generate_wish_text("Test Holiday")
            
            # Should return fallback
            assert result is not None
            assert "Test Holiday" in result
