"""Prometheus metrics collection for Mangalify bot monitoring."""

from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime

# Task execution metrics
daily_task_executions = Counter(
    'mangalify_daily_task_executions_total',
    'Total number of daily task executions',
    ['status']  # status: success, error
)

daily_task_duration = Histogram(
    'mangalify_daily_task_duration_seconds',
    'Duration of daily task execution',
    buckets=(0.5, 1, 2, 5, 10, 30, 60)
)

# Holiday processing metrics
holidays_processed = Counter(
    'mangalify_holidays_processed_total',
    'Total number of holidays processed',
    ['status']  # status: success, error
)

holidays_wishes_sent = Counter(
    'mangalify_holidays_wishes_sent_total',
    'Total holiday wishes sent to Discord'
)

# Birthday processing metrics
birthdays_processed = Counter(
    'mangalify_birthdays_processed_total',
    'Total number of birthdays processed',
    ['status']  # status: success, error
)

birthdays_wishes_sent = Counter(
    'mangalify_birthdays_wishes_sent_total',
    'Total birthday wishes sent to Discord'
)

# API metrics
api_calls = Counter(
    'mangalify_api_calls_total',
    'Total API calls to external services',
    ['service', 'status']  # service: gemini, calendarific; status: success, error
)

api_call_duration = Histogram(
    'mangalify_api_call_duration_seconds',
    'Duration of external API calls',
    ['service'],
    buckets=(0.1, 0.5, 1, 2, 5)
)

api_retries = Counter(
    'mangalify_api_retries_total',
    'Total API retries due to failures',
    ['service']
)

# Database metrics
database_operations = Counter(
    'mangalify_database_operations_total',
    'Total database operations',
    ['operation', 'status']  # operation: read, write, delete; status: success, error
)

database_operation_duration = Histogram(
    'mangalify_database_operation_duration_seconds',
    'Duration of database operations',
    ['operation'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1)
)

# Discord message metrics
discord_messages_sent = Counter(
    'mangalify_discord_messages_sent_total',
    'Total messages sent to Discord',
    ['channel_type']  # channel_type: birthday, holiday, alert, other
)

discord_messages_failed = Counter(
    'mangalify_discord_messages_failed_total',
    'Total failed Discord messages',
    ['channel_type']
)

# Bot metrics
bot_uptime = Gauge(
    'mangalify_bot_uptime_seconds',
    'Bot uptime in seconds'
)

bot_errors = Counter(
    'mangalify_bot_errors_total',
    'Total bot errors',
    ['error_type']
)

# Data health metrics
registered_birthdays = Gauge(
    'mangalify_registered_birthdays_total',
    'Total registered birthdays'
)

departed_members_cleanup = Counter(
    'mangalify_departed_members_cleanup_total',
    'Total departed members removed'
)

# Active session tracking
active_discord_members = Gauge(
    'mangalify_active_discord_members',
    'Number of active Discord members being tracked'
)


def record_task_start():
    """Record task start time for duration tracking."""
    return datetime.utcnow()


def record_task_end(start_time, status='success'):
    """Record task end and duration."""
    duration = (datetime.utcnow() - start_time).total_seconds()
    daily_task_executions.labels(status=status).inc()
    daily_task_duration.observe(duration)


def record_api_call(service, status='success', duration=None):
    """Record external API call."""
    api_calls.labels(service=service, status=status).inc()
    if duration:
        api_call_duration.labels(service=service).observe(duration)


def record_api_retry(service):
    """Record API retry."""
    api_retries.labels(service=service).inc()


def record_db_operation(operation, status='success', duration=None):
    """Record database operation."""
    database_operations.labels(operation=operation, status=status).inc()
    if duration:
        database_operation_duration.labels(operation=operation).observe(duration)


def record_holiday(status='success'):
    """Record holiday processing."""
    holidays_processed.labels(status=status).inc()


def record_wish_sent(wish_type='holiday'):
    """Record sent wish message."""
    if wish_type == 'holiday':
        holidays_wishes_sent.inc()
        discord_messages_sent.labels(channel_type='holiday').inc()
    elif wish_type == 'birthday':
        birthdays_wishes_sent.inc()
        discord_messages_sent.labels(channel_type='birthday').inc()


def record_birthday(status='success'):
    """Record birthday processing."""
    birthdays_processed.labels(status=status).inc()


def record_message_failed(channel_type='other'):
    """Record failed Discord message."""
    discord_messages_failed.labels(channel_type=channel_type).inc()


def record_error(error_type='unknown'):
    """Record bot error."""
    bot_errors.labels(error_type=error_type).inc()


def update_birthday_count(count):
    """Update total registered birthdays."""
    registered_birthdays.set(count)


def update_member_count(count):
    """Update active Discord members count."""
    active_discord_members.set(count)


def set_uptime(seconds):
    """Update bot uptime."""
    bot_uptime.set(seconds)
