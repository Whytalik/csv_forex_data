from calendar import week
from pathlib import Path
import pandas as pd  # type: ignore
from .base_metric import BaseMetric
from config.sessions_config import SESSIONS
from config.pairs_config import PAIRS
from services.utils import get_session_range


class VolatilityMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        daily_data = self.load_timeframe_data(symbol, year, "1d")
        weekly_data = self.load_timeframe_data(symbol, year, "1w")
        one_minute_data = self.load_timeframe_data(symbol, year, "1m")
        pip_factor = PAIRS[symbol.upper()]["pip_factor"]

        # Calculate daily metrics
        daily_range = round(
            ((daily_data["High"] - daily_data["Low"]) * pip_factor).mean(), 2
        )
        daily_body_size = round(
            (abs(daily_data["Close"] - daily_data["Open"]) * pip_factor).mean(), 2
        )

        # Calculate weekly metrics
        weekly_range = round(
            ((weekly_data["High"] - weekly_data["Low"]) * pip_factor).mean(), 2
        )
        weekly_body_size = round(
            (abs(weekly_data["Close"] - weekly_data["Open"]) * pip_factor).mean(), 2
        )

        # Calculate session ranges
        asia_range = get_session_range("Asia", one_minute_data, symbol)
        frankfurt_range = get_session_range("Frankfurt", one_minute_data, symbol)
        london_range = get_session_range("London", one_minute_data, symbol)
        lunch_range = get_session_range("Lunch", one_minute_data, symbol)
        ny_range = get_session_range("NY", one_minute_data, symbol)

        # Calculate daily ranges for each weekday
        daily_data_adjusted = daily_data.copy()
        daily_data_adjusted.index = daily_data_adjusted.index + pd.Timedelta(hours=3)

        weekday_ranges = {}
        for weekday in range(5):
            weekday_data = daily_data_adjusted[
                daily_data_adjusted.index.weekday == weekday
            ]
            if not weekday_data.empty:
                daily_ranges = (weekday_data["High"] - weekday_data["Low"]) * pip_factor
                weekday_ranges[weekday] = round(daily_ranges.mean(), 2)
            else:
                print(f"Warning: No data found for weekday {weekday}")
                weekday_ranges[weekday] = 0

        avg_monday_range = weekday_ranges[0]
        avg_tuesday_range = weekday_ranges[1]
        avg_wednesday_range = weekday_ranges[2]
        avg_thursday_range = weekday_ranges[3]
        avg_friday_range = weekday_ranges[4]

        metrics = {
            "Average Daily Range (pips)": daily_range,
            "Average Daily Body Size (pips)": daily_body_size,
            "Average Weekly Range (pips)": weekly_range,
            "Average Weekly Body Size (pips)": weekly_body_size,
            "Average Asia Range": asia_range,
            "Average Frankfurt Range": frankfurt_range,
            "Average London Range": london_range,
            "Average Lunch Range": lunch_range,
            "Average NY Range": ny_range,
            "Average Monday Range": avg_monday_range,
            "Average Tuesday Range": avg_tuesday_range,
            "Average Wednesday Range": avg_wednesday_range,
            "Average Thursday Range": avg_thursday_range,
            "Average Friday Range": avg_friday_range,
        }

        return metrics


class SessionDistributionMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes

        metrics = {
            "Daily High in Asia %": 0,  # TODO: Implement
            "Daily High in Frankfurt %": 0,  # TODO: Implement
            "Daily High in London %": 0,  # TODO: Implement
            "Daily High in Lunch %": 0,  # TODO: Implement
            "Daily High in NY %": 0,  # TODO: Implement
            "Daily High in Out of Session %": 0,  # TODO: Implement
            "Daily Low in Asia %": 0,  # TODO: Implement
            "Daily Low in Frankfurt %": 0,  # TODO: Implement
            "Daily Low in London %": 0,  # TODO: Implement
            "Daily Low in NY %": 0,  # TODO: Implement
            "Daily Low in Lunch %": 0,  # TODO: Implement
            "Daily Low in Out of Session %": 0,  # TODO: Implement
        }

        return metrics


class IntradayMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes

        metrics = {
            "Frankfurt-Asia High %": 0,  # TODO: Implement
            "Frankfurt-Asia Low %": 0,  # TODO: Implement
            # ... Add all other intraday metrics
        }

        return metrics


class DirectionalMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes

        metrics = {
            "Bullish Frankfurt-Asia Low %": 0,  # TODO: Implement
            "Bullish London-Asia Low %": 0,  # TODO: Implement
            # ... Add all other directional metrics
        }

        return metrics


class OccurrenceMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes
        daily_data = self.load_timeframe_data(symbol, year, "1d")

        metrics = {
            "High in Monday": 0,  # TODO: Implement
            "High in Tuesday": 0,  # TODO: Implement
            # ... Add all other occurrence metrics
        }

        return metrics
