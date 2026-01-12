# Mangalify

A Discord bot for automating birthday wishes and holiday greetings.

## Features

- **Birthday Automation**: Users register birthdays via slash commands. The bot assigns a birthday role and posts a wish message at midnight.
- **Holiday Greetings**: Checks daily for holidays (via Calendarific) and generates custom wish text using AI (Google Gemini).
- **Staff Controls**: Commands to manually trigger posts, export data, and manage departed members.
- **Monitoring**: Built-in Prometheus metrics for health tracking and Sentry for error reporting.

## Setup Instructions

### 1. Prerequisites
- Discord Bot Token via [Discord Developer Portal](https://discord.com/developers/applications)
- MongoDB instance (local or cloud)
- Google Gemini API Key
- Calendarific API Key

### 2. Configuration
Create a `.env` file in the root directory:

```env
# Credentials
DISCORD_BOT_TOKEN=your_token_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=mangalify
GEMINI_API_KEY=your_gemini_key
CALENDARIFIC_API_KEY=your_calendarific_key

# Optional Monitoring
SENTRY_DSN=your_sentry_dsn
METRICS_PORT=8000

# Server Config
GUILD_ID=your_server_id
TIMEZONE=Asia/Kolkata
DAILY_TRIGGER_TIME=00:00

# Channels & Roles
WISHES_CHANNEL_ID=channel_id_for_holidays
BIRTHDAY_CHANNEL_ID=channel_id_for_birthdays
STAFF_ALERTS_CHANNEL_ID=channel_id_for_logs
BIRTHDAY_ROLE_ID=role_id_for_users
STAFF_ROLE_ID=role_id_for_admins
```

### 3. Run with Docker (Recommended)
This starts the bot, MongoDB database, and Prometheus monitoring.

```bash
docker-compose up -d
```

- Bot Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090

### 4. Run Locally
Install dependencies and start the bot.

```bash
# Install requirements
pip install -r requirements.txt

# Run bot
python main.py
```

---

See [DEPLOYMENT.md](DEPLOYMENT.md) for server deployment and [API.md](API.md) for command documentation.