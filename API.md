# Mangalify API Documentation

Complete reference for Mangalify's internal APIs, commands, and integration points.

## Table of Contents

- [Discord Commands](#discord-commands)
- [Database Schema](#database-schema)
- [Internal APIs](#internal-apis)
- [External APIs](#external-apis)
- [Environment Configuration](#environment-configuration)
- [Logging](#logging)

## Discord Commands

### Birthday Commands (`/birthday`)

| Command | Parameters | Permission | Description |
|---------|-----------|------------|-------------|
| `/birthday set` | `day`, `month`, `year` | User | Register your birthday |
| `/birthday remove` | - | User | Remove your birthday |
| `/birthday check` | - | User | View your registered birthday |
| `/birthday list` | - | Staff | List all registered birthdays |
| `/birthday export` | - | Staff | Export birthdays to JSON |
| `/birthday import_json` | `file` | Staff | Import birthdays from JSON |
| `/birthday cleanup_departed` | - | Staff | Remove departed members |

#### Example Usage

```python
# User registering birthday
/birthday set day:15 month:3 year:1995

# Staff exporting data
/birthday export
# Returns: birthdays_export_2026-01-06.json
```

### Holiday Commands

| Command | Parameters | Permission | Description |
|---------|-----------|------------|-------------|
| `/holiday_post` | `holiday_name` | Staff | Manually post pending holiday wish |

#### Example Usage

```python
# Post approved holiday wish
/holiday_post holiday_name:"Republic Day"
```

### Help Commands

| Command | Parameters | Permission | Description |
|---------|-----------|------------|-------------|
| `/help` | - | User | Show all commands and features |
| `/about` | - | User | Show bot information and stats |

---

## Database Schema

### Collections

#### `birthdays`

Stores user birthday information.

```python
{
    "_id": 123456789012345678,  # Discord user ID (int)
    "day": 15,                   # Day of month (1-31)
    "month": 3,                  # Month (1-12)
    "year": 1995                 # Birth year (optional, int or null)
}
```

**Indexes:**
- Compound index on `(day, month)` for efficient date queries

#### `birthday_role_log`

Tracks birthday role assignments.

```python
{
    "_id": ObjectId("..."),
    "user_id": 123456789012345678,  # Discord user ID
    "date_added": "2026-01-06"      # ISO date string (YYYY-MM-DD)
}
```

**Indexes:**
- Index on `date_added` for cleanup operations

#### `scheduler_meta`

Stores scheduler state for persistence.

```python
{
    "_id": "daily_task_last_run",   # Unique identifier
    "timestamp": "2026-01-06T00:00:00Z",  # ISO 8601 timestamp
    "status": "success",             # "success" | "error"
    "details": "Processed 5 birthdays, 2 holidays"  # Summary string
}
```

---

## Internal APIs

### Database Manager (`utils/db_manager.py`)

#### Birthday Operations

```python
async def set_birthday(user_id: int, day: int, month: int, year: int | None) -> None:
    """Set or update user's birthday."""

async def get_birthday(user_id: int) -> dict | None:
    """Retrieve user's birthday data."""

async def delete_birthday(user_id: int) -> None:
    """Remove user's birthday."""

def get_birthdays_for_date(day: int, month: int) -> AsyncGenerator:
    """Get all birthdays for a specific date."""
    # Yields: {"_id": user_id, "day": day, "month": month, "year": year}

def get_all_birthdays() -> AsyncGenerator:
    """Get all registered birthdays."""
    # Yields: {"_id": user_id, "day": day, "month": month, "year": year}
```

#### Role Log Operations

```python
async def add_user_to_role_log(user_id: int, date_str: str) -> None:
    """Add user to birthday role log."""

async def remove_user_from_role_log(user_id: int) -> None:
    """Remove user from birthday role log."""

async def get_all_in_role_log() -> list[dict]:
    """Get all users in role log."""
    # Returns: [{"user_id": 123, "date_added": "2026-01-06"}, ...]
```

#### Scheduler Operations

```python
async def set_scheduler_meta(key: str, value: str, details: str) -> None:
    """Update scheduler metadata."""

async def get_scheduler_meta(key: str) -> dict | None:
    """Get scheduler metadata."""
    # Returns: {"timestamp": "...", "status": "...", "details": "..."}
```

#### Utility Operations

```python
async def ensure_indexes() -> None:
    """Create database indexes if they don't exist."""

async def get_all_birthdays_list() -> list[dict]:
    """Get all birthdays as a list (for export)."""
```

### API Client (`utils/api_client.py`)

#### Gemini AI

```python
async def generate_wish_text(holiday_name: str) -> str:
    """Generate holiday wish using Gemini AI.
    
    Args:
        holiday_name: Name of the holiday
        
    Returns:
        Generated wish message (max 200 chars)
        Fallback message if API fails after 3 retries
    """

async def generate_birthday_wish_text(name: str, mention: str) -> str:
    """Generate personalized birthday wish.
    
    Args:
        name: User's display name
        mention: User's Discord mention (@user)
        
    Returns:
        Generated birthday message (max 200 chars)
        Fallback message if API fails after 3 retries
    """
```

#### Calendarific API

```python
async def get_holidays(year: int, month: int) -> list[dict] | None:
    """Fetch holidays for a specific month.
    
    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        
    Returns:
        List of holidays or None if API fails
        [
            {
                "name": "Republic Day",
                "date": {"iso": "2026-01-26"},
                "description": "...",
                "type": ["National holiday"]
            },
            ...
        ]
    """
```

#### Retry Mechanism

All API calls use exponential backoff:
- **Base delay**: 0.5 seconds
- **Max retries**: 3
- **Backoff formula**: `base_delay * (2 ** attempt)`
- **Total max delay**: ~3.5 seconds (0.5s + 1s + 2s)

### Wishes Cog (`cogs/wishes.py`)

#### Daily Task

```python
@tasks.loop(time=datetime.time(hour=0, minute=0))  # Configured via DAILY_TRIGGER_TIME
async def daily_task():
    """Main scheduled task for birthday/holiday checks.
    
    Runs daily at configured time (default 00:00 IST).
    Persists last run time and summary to database.
    """
```

#### Internal Methods

```python
async def _check_for_holidays(today: datetime) -> int:
    """Check and announce holidays.
    
    Returns:
        Number of holidays processed
    """

async def _check_for_birthdays(today: datetime) -> int:
    """Check and announce birthdays.
    
    Returns:
        Number of birthdays processed
    """

async def _cleanup_departed_members() -> int:
    """Remove birthdays for departed members.
    
    Returns:
        Number of members removed
    """

def _guard_message(message: str) -> str:
    """Apply profanity filter and length cap.
    
    Args:
        message: Raw message from AI
        
    Returns:
        Sanitized message (censored profanity, max 200 chars)
    """
```

---

## External APIs

### Google Gemini API

**Endpoint**: `generativelanguage.googleapis.com`

**Model**: `gemini-1.5-flash-latest`

**Rate Limits**: 15 requests per minute (free tier)

**Request Example**:
```python
{
    "contents": [{
        "parts": [{
            "text": "Generate a short festive wish for Diwali in 200 characters or less."
        }]
    }]
}
```

**Response Example**:
```python
{
    "candidates": [{
        "content": {
            "parts": [{
                "text": "Wishing you a joyous Diwali filled with light..."
            }]
        }
    }]
}
```

### Calendarific API

**Endpoint**: `calendarific.com/api/v2/holidays`

**Rate Limits**: 1000 requests/month (free tier)

**Request Parameters**:
- `api_key`: Your API key
- `country`: `IN` (India)
- `year`: e.g., `2026`
- `month`: `1-12`

**Response Example**:
```python
{
    "response": {
        "holidays": [
            {
                "name": "Republic Day",
                "description": "Republic Day is a public holiday...",
                "date": {
                    "iso": "2026-01-26",
                    "datetime": {"year": 2026, "month": 1, "day": 26}
                },
                "type": ["National holiday"],
                "locations": "All",
                "states": "All"
            }
        ]
    }
}
```

---

## Environment Configuration

### Required Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `DISCORD_BOT_TOKEN` | string | Discord bot token | `MTIzNDU2Nzg5MA...` |
| `GUILD_ID` | int | Discord server ID | `123456789012345678` |
| `BIRTHDAY_CHANNEL_ID` | int | Birthday announcements channel | `123456789012345678` |
| `WISHES_CHANNEL_ID` | int | Holiday wishes channel | `123456789012345678` |
| `STAFF_ALERTS_CHANNEL_ID` | int | Staff alerts channel | `123456789012345678` |
| `BIRTHDAY_ROLE_ID` | int | Birthday role ID | `123456789012345678` |
| `MONGO_URI` | string | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | string | Database name | `mangalify` |
| `GEMINI_API_KEY` | string | Google Gemini API key | `AIzaSy...` |
| `CALENDARIFIC_API_KEY` | string | Calendarific API key | `abc123...` |
| `DAILY_TRIGGER_TIME` | string | Daily task time (HH:MM) | `00:00` |
| `TIMEZONE` | string | Timezone for scheduling | `Asia/Kolkata` |

### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | string | `plain` | `plain` or `json` |
| `HOLIDAY_APPROVAL_MODE` | bool | `false` | Require manual holiday posting |
| `LOAD_DOTENV` | bool | `true` | Load .env file (set `false` for tests) |

---

## Logging

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures, exceptions)

### Log Formats

#### Plain Text Format

```
2026-01-06 00:00:15 INFO Daily task starting for 2026-01-06
2026-01-06 00:00:16 INFO Holiday check: Found 1 holiday(s): Republic Day
2026-01-06 00:00:17 INFO Birthday check: Found 2 birthday(s)
```

#### JSON Format

```json
{
  "timestamp": "2026-01-06T00:00:15Z",
  "level": "INFO",
  "message": "Daily task starting for 2026-01-06",
  "event": "daily_task_start",
  "date": "2026-01-06"
}
```

### Structured Logging Fields

Common fields in JSON logs:

| Field | Description | Example |
|-------|-------------|---------|
| `event` | Event identifier | `holiday_found`, `birthday_announced` |
| `user_id` | Discord user ID | `123456789012345678` |
| `holiday_name` | Holiday name | `Republic Day` |
| `error_type` | Error class name | `HTTPException` |
| `retry_count` | Current retry attempt | `2` |
| `year`, `month`, `day` | Date components | `2026`, `1`, `6` |

### Log Rotation

Logs are written to:
- **stdout/stderr** (captured by Docker/systemd)
- **File logging** (if configured)

Recommended rotation:
```bash
# logrotate configuration
/var/log/mangalify/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
}
```

---

## Error Handling

### Common Error Codes

| Error | Cause | Resolution |
|-------|-------|------------|
| `MissingRequiredArgument` | Missing command parameter | Check command syntax |
| `BadArgument` | Invalid parameter type | Provide correct type (e.g., int, date) |
| `CheckFailure` | Permission denied | Ensure user has required role |
| `HTTPException` | Discord API error | Check rate limits, retry |
| `ConnectionError` | External API unreachable | Check network, API status |

### Retry Strategy

- **API calls**: Exponential backoff (3 retries)
- **Database ops**: Single attempt (MongoDB driver handles reconnection)
- **Discord commands**: Single attempt (user notified of errors)

---

## Integration Examples

### Custom Command

```python
from discord import app_commands
from discord.ext import commands

class CustomCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command()
    async def my_command(self, interaction: discord.Interaction):
        """Custom command example."""
        await interaction.response.send_message("Hello!")

async def setup(bot):
    await bot.add_cog(CustomCog(bot))
```

### Database Query

```python
from utils.db_manager import get_birthdays_for_date

async def get_january_birthdays():
    """Get all birthdays in January."""
    birthdays = []
    for day in range(1, 32):
        cursor = get_birthdays_for_date(day, 1)
        async for bd in cursor:
            birthdays.append(bd)
    return birthdays
```

### AI Wish Generation

```python
from utils.api_client import api_client

async def generate_custom_wish(event_name: str):
    """Generate custom event wish."""
    wish = await api_client.generate_wish_text(event_name)
    return wish
```

---

## Performance Considerations

### Database Optimization

- **Indexes**: Queries use compound index `(day, month)` for O(log n) lookups
- **Connection pooling**: Motor handles connection reuse automatically
- **Async operations**: All DB ops are non-blocking

### API Rate Limits

- **Gemini**: 15 req/min (free tier) - daily task processes ~20-30 events/day
- **Calendarific**: 1000 req/month - fetches 12 months = 12 requests
- **Discord**: 50 req/sec - unlikely to hit with current usage

### Memory Usage

- **Bot process**: ~50-100 MB RAM
- **MongoDB**: ~500 MB RAM (depends on data size)
- **Docker container**: ~200 MB total (slim image)

---

## Security Best Practices

1. **Never commit `.env` files** - use `.env.example` template
2. **Rotate API keys** regularly
3. **Use least-privilege** MongoDB user (not admin)
4. **Enable Discord bot permissions** carefully
5. **Validate user input** in custom commands
6. **Use HTTPS** for external API calls (default)
7. **Run as non-root** user in Docker/systemd

---

## Monitoring

### Health Checks

```bash
# Docker health check
docker ps --filter name=mangalify --format "{{.Status}}"

# Systemd status
sudo systemctl status mangalify

# Check logs
docker logs -f mangalify-bot
journalctl -u mangalify -f
```

### Metrics to Monitor

- **Bot uptime**: Should restart on failure
- **Task execution**: Check `scheduler_meta` collection
- **Error rate**: Monitor ERROR logs
- **API success rate**: Check WARNING logs for API failures
- **Database size**: Monitor document count growth

---

## Support

- **Issues**: [GitHub Issues](https://github.com/PRADDZY/Mangalify/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PRADDZY/Mangalify/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Last Updated: January 6, 2026*
