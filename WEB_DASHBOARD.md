# Web Dashboard Guide

## Overview

The Mangalify Web Dashboard is a powerful web-based interface for managing your Discord bot. It provides analytics, birthday management, and custom wish management through an intuitive web interface.

## Features

### 📊 Analytics
- View total birthdays registered
- Track custom wishes count
- See upcoming birthdays (7-day and 30-day views)
- Birthday distribution by month chart
- Real-time statistics

### 🎂 Birthday Management
- Browse all registered birthdays
- View user ID, birthday date, and age
- Delete birthday entries
- Clean, sortable table interface

### 💝 Wish Management
- View all custom wishes
- Display wish details (name, date, message, role)
- Delete wish entries
- Organized table view

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB database running
- Flask and dependencies installed

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   
   Add to your `.env` file:
   ```env
   # Required
   MONGO_URI=your_mongodb_connection_string
   WEB_ADMIN_PASSWORD=your-secure-password
   
   # Optional (with defaults)
   WEB_PORT=5000
   WEB_HOST=0.0.0.0
   WEB_DEBUG=False
   WEB_SECRET_KEY=change-this-in-production
   ```

3. **Run the dashboard**
   ```bash
   python run_web.py
   ```
   
   Or directly:
   ```bash
   python web/app.py
   ```

4. **Access the dashboard**
   
   Open your browser to: `http://localhost:5000`
   
   Login with your configured `WEB_ADMIN_PASSWORD`

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MONGO_URI` | MongoDB connection string | Yes | - |
| `WEB_ADMIN_PASSWORD` | Admin password for login | Yes | admin |
| `WEB_SECRET_KEY` | Flask session secret key | No | auto-generated |
| `WEB_PORT` | Port to run the server on | No | 5000 |
| `WEB_HOST` | Host address to bind to | No | 0.0.0.0 |
| `WEB_DEBUG` | Enable Flask debug mode | No | False |

### Security Best Practices

1. **Strong Password**: Always use a strong, unique password for `WEB_ADMIN_PASSWORD`
   ```bash
   # Generate a random password on Linux/Mac
   openssl rand -base64 32
   ```

2. **Secret Key**: Set a random secret key in production
   ```bash
   # Generate a random secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **HTTPS**: Use a reverse proxy (nginx/Apache) with SSL/TLS certificates for production

4. **Firewall**: Restrict access using firewall rules
   ```bash
   # Example: Allow only from specific IP
   sudo ufw allow from 192.168.1.0/24 to any port 5000
   ```

## API Endpoints

The dashboard exposes RESTful API endpoints for programmatic access:

### Authentication Required

All endpoints require login session authentication.

### Endpoints

#### GET /api/stats
Returns dashboard statistics.

**Response:**
```json
{
  "total_birthdays": 42,
  "total_wishes": 5,
  "birthdays_by_month": [
    {"_id": 1, "count": 5},
    {"_id": 2, "count": 3}
  ],
  "upcoming_birthdays": [
    {
      "_id": 123456789,
      "day": 15,
      "month": 3,
      "year": 1995,
      "days_until": 5
    }
  ]
}
```

#### GET /api/birthdays
Returns all registered birthdays.

**Response:**
```json
[
  {
    "_id": 123456789,
    "day": 15,
    "month": 3,
    "year": 1995
  }
]
```

#### DELETE /api/birthdays/<user_id>
Deletes a birthday entry.

**Response:**
```json
{
  "success": true
}
```

#### GET /api/wishes
Returns all custom wishes.

**Response:**
```json
[
  {
    "_id": "abc123",
    "name": "Christmas",
    "day": 25,
    "month": 12,
    "year": 2024,
    "message": "Merry Christmas!",
    "role_id": "everyone"
  }
]
```

#### DELETE /api/wishes/<wish_id>
Deletes a custom wish.

**Response:**
```json
{
  "success": true
}
```

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
   ```

### Using nginx Reverse Proxy

1. **Create nginx configuration**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Enable SSL with Let's Encrypt**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

### Using Systemd Service

1. **Create service file** `/etc/systemd/system/mangalify-web.service`
   ```ini
   [Unit]
   Description=Mangalify Web Dashboard
   After=network.target
   
   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/Mangalify
   ExecStart=/usr/bin/python3 run_web.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service**
   ```bash
   sudo systemctl enable mangalify-web
   sudo systemctl start mangalify-web
   ```

## Troubleshooting

### Cannot connect to MongoDB
**Error:** `MONGO_URI not found in environment variables`

**Solution:** Ensure `MONGO_URI` is set in your `.env` file:
```env
MONGO_URI=mongodb://localhost:27017/wishes_bot_db
```

### Login fails
**Issue:** Invalid password error

**Solution:** 
1. Check `WEB_ADMIN_PASSWORD` in `.env`
2. Restart the web server after changing the password
3. Clear browser cookies/cache

### Port already in use
**Error:** `Address already in use`

**Solution:**
1. Change `WEB_PORT` to a different port
2. Or stop the process using the port:
   ```bash
   # Find process
   sudo lsof -i :5000
   # Kill process
   kill -9 <PID>
   ```

### Charts not loading
**Issue:** Birthday by month chart not displaying

**Solution:** 
- Check browser console for errors
- Ensure internet connection (Chart.js loads from CDN)
- Check browser ad-blocker settings

## Development

### Project Structure
```
web/
├── __init__.py           # Module initialization
├── app.py                # Main Flask application
├── static/               # Static files (future)
└── templates/            # HTML templates
    ├── base.html         # Base template with layout
    ├── index.html        # Dashboard home
    ├── login.html        # Login page
    ├── analytics.html    # Analytics page
    ├── birthdays.html    # Birthday management
    └── wishes.html       # Wish management
```

### Adding New Features

1. **Add a new route** in `web/app.py`:
   ```python
   @app.route('/my-feature')
   @login_required
   def my_feature():
       return render_template('my-feature.html')
   ```

2. **Create template** in `web/templates/my-feature.html`:
   ```html
   {% extends "base.html" %}
   {% block content %}
   <!-- Your content here -->
   {% endblock %}
   ```

3. **Add database methods** in `utils/db_manager.py`:
   ```python
   async def get_my_data(self):
       return await self.collection.find({}).to_list(length=None)
   ```

## Support

For issues or questions:
1. Check the [main README](README.md)
2. Review [GitHub Issues](https://github.com/PRADDZY/Mangalify/issues)
3. Create a new issue with detailed information

## License

Same as the main project - MIT License
