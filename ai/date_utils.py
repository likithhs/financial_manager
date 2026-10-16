"""
Date & Timezone Utilities for Finora Financial Manager.
Ensures consistent calendar-month date filtering, boundary handling, and timezone awareness.
"""

import os
from datetime import date, datetime
import calendar


def get_app_timezone():
    """
    Returns the configured application timezone or None for system local.
    Checks APP_TIMEZONE and TIMEZONE environment variables.
    """
    tz_name = (os.environ.get('APP_TIMEZONE', '').strip() or 
               os.environ.get('TIMEZONE', '').strip())
    if tz_name:
        try:
            import zoneinfo
            return zoneinfo.ZoneInfo(tz_name)
        except Exception:
            pass
    return None


def get_app_current_date():
    """
    Returns the current date respecting configured timezone or system local time.
    """
    tz = get_app_timezone()
    if tz:
        return datetime.now(tz).date()
    # Uses system local timezone with offset awareness
    return datetime.now().astimezone().date()


def get_calendar_month_range(target_date=None):
    """
    Given a target_date (date object, datetime object, or 'YYYY-MM' / 'YYYY-MM-DD' string),
    returns (first_day, last_day) as date objects.
    Defaults to current calendar month using the app's current date.
    Safely handles leap years, month boundaries (e.g. 28/29/30/31 days), and year transitions.
    """
    if target_date is None:
        target_date = get_app_current_date()
    elif isinstance(target_date, str):
        target_date = target_date.strip()
        if len(target_date) == 7:  # 'YYYY-MM'
            target_date = datetime.strptime(target_date, '%Y-%m').date()
        else:
            target_date = datetime.strptime(target_date[:10], '%Y-%m-%d').date()
    elif isinstance(target_date, datetime):
        target_date = target_date.date()

    first_day = date(target_date.year, target_date.month, 1)
    _, last_day_num = calendar.monthrange(target_date.year, target_date.month)
    last_day = date(target_date.year, target_date.month, last_day_num)
    return first_day, last_day
