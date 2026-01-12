# Deployment Guide

Get Mangalify running in production.

## 🐳 Docker (Recommended)

1. **Clone & Config**:
   ```bash
   git clone https://github.com/PRADDZY/Mangalify.git
   cp .env.example .env
   # Fill in .env details
   ```

2. **Run**:
   ```bash
   docker-compose up -d
   ```

3. **Manage**:
   - Logs: `docker logs -f mangalify-bot`
   - Restart: `docker-compose restart`

## 🐧 Linux Service (Systemd)

If you hate Docker, do this:

1. **Setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Service File** (`/etc/systemd/system/mangalify.service`):
   ```ini
   [Service]
   ExecStart=/path/to/venv/bin/python main.py
   WorkingDirectory=/path/to/mangalify
   Restart=always
   User=your_user
   ```

3. **Start**:
   ```bash
   sudo systemctl enable --now mangalify
   ```
