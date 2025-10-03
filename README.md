# Mangalify 🎉

A Discord bot designed to bring joy and celebration to your server by automatically managing birthday wishes, festival greetings, and special occasion messages.

## ✨ Features

### 🎂 Birthday Management
- **Set Birthdays**: Users can set their birthdays using slash commands
- **Automatic Wishes**: Bot automatically sends birthday wishes at a configured time
- **Birthday Role**: Assigns special birthday role to users on their special day
- **Staff Notifications**: Alerts staff members about upcoming birthdays

### 🎊 Festival Greetings
- **Holiday Detection**: Automatically detects holidays and festivals using Calendarific API
- **Custom Wishes**: Generates personalized festival greetings using Google Gemini AI
- **Multi-language Support**: Supports multiple languages for diverse communities
- **Scheduled Posts**: Posts festival wishes at configured times

### 🛠️ Staff Tools
- **Manual Wishes**: Staff can create and send custom wishes through modals
- **Birthday Management**: View and manage user birthdays
- **Channel Configuration**: Dedicated channels for different types of announcements

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Application with Bot Token
- MongoDB Database
- Google Gemini API Key (optional, for AI-generated wishes)
- Calendarific API Key (optional, for holiday detection)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PRADDZY/Mangalify.git
   cd Mangalify
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Discord Configuration
   BOT_TOKEN=your_discord_bot_token
   GUILD_ID=your_server_id
   STAFF_ROLE_ID=your_staff_role_id
   BIRTHDAY_ROLE_ID=your_birthday_role_id
   
   # Channel IDs
   WISHES_CHANNEL_ID=your_wishes_channel_id
   BIRTHDAY_CHANNEL_ID=your_birthday_channel_id
   STAFF_ALERTS_CHANNEL_ID=your_staff_alerts_channel_id
   
   # Timing Configuration
   POST_TIME_UTC=00:01
   SERVER_TIMEZONE=UTC
   
   # API Keys (Optional)
   GEMINI_API_KEY=your_gemini_api_key
   CALENDARIFIC_API_KEY=your_calendarific_api_key
   CALENDARIFIC_COUNTRY_CODE=US
   
   # Database
   MONGODB_URI=your_mongodb_connection_string
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

5. **Run the web dashboard (optional)**
   ```bash
   python web/app.py
   ```
   
   Then access the dashboard at `http://localhost:5000`

## 📖 Usage

### For Users
- `/birthday set <day> <month> <year>` - Set your birthday
- `/birthday remove` - Remove your birthday from the database
- `/birthday view` - View your current birthday setting

### For Staff
- Use the wish modal system to create custom birthday and festival messages
- Monitor the staff alerts channel for birthday notifications
- Manage birthday roles and announcements

### Web Dashboard
- Access the web management interface at `http://localhost:5000` (or your configured host/port)
- View analytics and statistics
- Manage birthdays and custom wishes
- Monitor upcoming celebrations

## 🏗️ Project Structure

```
Mangalify/
├── main.py                 # Bot entry point and setup
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── cogs/
│   ├── __init__.py
│   ├── birthdays.py       # Birthday management commands
│   └── wishes.py          # Wish system and automated posting
├── utils/
│   ├── __init__.py
│   ├── api_client.py      # External API integrations
│   └── db_manager.py      # Database operations
├── web/
│   ├── app.py             # Flask web application
│   ├── templates/         # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── analytics.html
│   │   ├── birthdays.html
│   │   └── wishes.html
│   └── static/            # Static files (CSS, JS, images)
└── tests/
    └── test.py            # Unit tests
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Discord bot token | Yes | - |
| `GUILD_ID` | Discord server ID | Yes | - |
| `STAFF_ROLE_ID` | Staff role ID for permissions | Yes | - |
| `BIRTHDAY_ROLE_ID` | Role assigned on birthdays | Yes | - |
| `WISHES_CHANNEL_ID` | Channel for birthday wishes | Yes | - |
| `BIRTHDAY_CHANNEL_ID` | Channel for birthday announcements | Yes | - |
| `STAFF_ALERTS_CHANNEL_ID` | Channel for staff notifications | Yes | - |
| `POST_TIME_UTC` | Time to post wishes (HH:MM) | No | 00:01 |
| `SERVER_TIMEZONE` | Server timezone | No | UTC |
| `GEMINI_API_KEY` | Google Gemini API key | No | - |
| `CALENDARIFIC_API_KEY` | Calendarific API key | No | - |
| `CALENDARIFIC_COUNTRY_CODE` | Country code for holidays | No | US |
| `WEB_PORT` | Web dashboard port | No | 5000 |
| `WEB_HOST` | Web dashboard host | No | 0.0.0.0 |
| `WEB_DEBUG` | Enable Flask debug mode | No | False |
| `WEB_SECRET_KEY` | Secret key for web sessions | Yes (for web) | - |
| `WEB_ADMIN_PASSWORD` | Admin password for dashboard | Yes (for web) | admin |

### Setting up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable the following bot permissions:
   - Send Messages
   - Use Slash Commands
   - Manage Roles
   - Read Message History
   - View Channels

### Web Dashboard Setup

The web dashboard provides a user-friendly interface for managing your bot:

**Features:**
- 📊 **Analytics Dashboard**: View comprehensive statistics about birthdays, wishes, and upcoming events
- 🎂 **Birthday Management**: Browse and manage all registered birthdays
- 💝 **Wish Management**: View and delete custom wishes
- 🔒 **Secure Access**: Password-protected admin interface

**Access:**
1. Set `WEB_ADMIN_PASSWORD` in your `.env` file
2. Run `python web/app.py`
3. Open your browser to `http://localhost:5000`
4. Login with your admin password

**Security Notes:**
- Always use a strong password for `WEB_ADMIN_PASSWORD`
- Set `WEB_SECRET_KEY` to a random string in production
- Consider using a reverse proxy (nginx/Apache) if exposing to the internet
- Enable HTTPS for production deployments

## 🧪 Testing

Run the test suite:
```bash
python -m pytest test.py -v
```

Or run with coverage:
```bash
python -m pytest test.py --cov=. --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/PRADDZY/Mangalify/issues) page
2. Create a new issue with detailed information
3. Join our support Discord server (if available)

## 🙏 Acknowledgments

- Discord.py community for the excellent library
- Google Gemini AI for intelligent wish generation
- Calendarific for holiday data
- All contributors who help make this project better

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/PRADDZY/Mangalify?style=social)
![GitHub forks](https://img.shields.io/github/forks/PRADDZY/Mangalify?style=social)
![GitHub issues](https://img.shields.io/github/issues/PRADDZY/Mangalify)
![GitHub license](https://img.shields.io/github/license/PRADDZY/Mangalify)

---

Made with ❤️ for bringing joy to Discord communities