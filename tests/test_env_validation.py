import importlib
import os
import sys
import pytest

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def reload_main():
    """Reload main module to ensure fresh globals for each test."""
    if "main" in sys.modules:
        del sys.modules["main"]
    return importlib.import_module("main")


def test_validate_environment_success(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("GUILD_ID", "1")
    monkeypatch.setenv("STAFF_ROLE_ID", "2")
    monkeypatch.setenv("BIRTHDAY_ROLE_ID", "3")
    monkeypatch.setenv("WISHES_CHANNEL_ID", "4")
    monkeypatch.setenv("BIRTHDAY_CHANNEL_ID", "5")
    monkeypatch.setenv("STAFF_ALERTS_CHANNEL_ID", "6")
    monkeypatch.setenv("POST_TIME_UTC", "05:30")

    main = reload_main()
    # Should not raise
    main.validate_environment()
    assert main.BOT_TOKEN == "token"
    assert main.GUILD_ID == 1


def test_validate_environment_missing(monkeypatch):
    # Unset required vars
    for key in [
        "BOT_TOKEN",
        "GUILD_ID",
        "STAFF_ROLE_ID",
        "BIRTHDAY_ROLE_ID",
        "WISHES_CHANNEL_ID",
        "BIRTHDAY_CHANNEL_ID",
        "STAFF_ALERTS_CHANNEL_ID",
    ]:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("POST_TIME_UTC", "00:01")

    main = reload_main()
    with pytest.raises(SystemExit):
        main.validate_environment()


def test_validate_environment_invalid_time(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("GUILD_ID", "1")
    monkeypatch.setenv("STAFF_ROLE_ID", "2")
    monkeypatch.setenv("BIRTHDAY_ROLE_ID", "3")
    monkeypatch.setenv("WISHES_CHANNEL_ID", "4")
    monkeypatch.setenv("BIRTHDAY_CHANNEL_ID", "5")
    monkeypatch.setenv("STAFF_ALERTS_CHANNEL_ID", "6")
    monkeypatch.setenv("POST_TIME_UTC", "invalid")

    main = reload_main()
    with pytest.raises(SystemExit):
        main.validate_environment()
