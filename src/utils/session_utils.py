"""
Утиліти для роботи з торговими сесіями
"""

import pandas as pd
from config.pairs_config import PAIRS
from config.sessions_config import SESSIONS


def get_session_range(session_name: str, data: pd.DataFrame, symbol: str) -> float:
    """
    Calculate price range for a specific trading session

    :param session_name: Name of the session from SESSIONS config
    :param data: DataFrame with OHLC price data (must have datetime index)
    :param symbol: Trading symbol (e.g. 'EURUSD')
    :return: Average session range in pips
    """
    if data.empty:
        return 0.0

    session = SESSIONS[session_name]
    start_time = pd.to_datetime(session["start"]).time()
    end_time = pd.to_datetime(session["end"]).time()
    pip_factor = PAIRS[symbol.upper()]["pip_factor"]

    # Handle sessions that cross midnight
    if start_time > end_time:
        mask = (data.index.time >= start_time) | (data.index.time < end_time)
    else:
        mask = (data.index.time >= start_time) & (data.index.time < end_time)

    session_data = data[mask]
    if session_data.empty:
        return 0.0  # Group by date to get daily session ranges
    session_data = session_data.groupby(session_data.index.date).agg(
        {"High": "max", "Low": "min"}
    )

    return round(((session_data["High"] - session_data["Low"]) * pip_factor).mean(), 2)


def is_time_in_session(time_to_check, session_times):
    """
    Checks if a time belongs to the specified session

    :param time_to_check: Time to check (datetime.time object)
    :param session_times: Dictionary with session start and end times
    :return: True if time is in session, False otherwise
    """
    start_time = pd.to_datetime(session_times["start"]).time()
    end_time = pd.to_datetime(session_times["end"]).time()

    # Handle sessions that cross midnight
    if start_time > end_time:
        return time_to_check >= start_time or time_to_check < end_time
    else:
        return start_time <= time_to_check < end_time
