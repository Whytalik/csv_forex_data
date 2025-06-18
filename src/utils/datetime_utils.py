import datetime
import pytz


def determine_day_start_hour(date: datetime.datetime) -> int:
    eastern = pytz.timezone("US/Eastern")

    if date.tzinfo is None:
        date = pytz.utc.localize(date)

    date_eastern = date.astimezone(eastern)
    is_dst = date_eastern.dst() != datetime.timedelta(0)
    return 21 if is_dst else 22


def get_forex_week_start(date: datetime.datetime) -> datetime.datetime:
    if date.tzinfo is None:
        date = pytz.utc.localize(date)

    start_hour = determine_day_start_hour(date)
    weekday = date.weekday()

    days_to_subtract = weekday + 1
    if weekday == 6 and date.hour >= start_hour:
        days_to_subtract = 0

    sunday = date - datetime.timedelta(days=days_to_subtract)
    week_start = sunday.replace(hour=start_hour, minute=0, second=0, microsecond=0)

    return week_start


def get_forex_trading_date(timestamp: datetime.datetime) -> datetime.date:
    if timestamp.tzinfo is None:
        timestamp = pytz.utc.localize(timestamp)

    day_start_hour = determine_day_start_hour(timestamp)
    weekday = timestamp.weekday()

    if weekday == 6:
        return (timestamp + datetime.timedelta(days=1)).date()

    if timestamp.hour >= day_start_hour:
        return (timestamp + datetime.timedelta(days=1)).date()
    else:
        return timestamp.date()
