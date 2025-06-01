from calendar import week
from pathlib import Path
import pandas as pd
from .base_metric import BaseMetric
from config.sessions_config import SESSIONS
from config.pairs_config import PAIRS


class VolatilityMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        daily_data = self.load_timeframe_data(symbol, year, "1d")
        weekly_data = self.load_timeframe_data(symbol, year, "1w")
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

        metrics = {
            "Average Daily Range (pips)": daily_range,
            "Average Daily Body Size (pips)": daily_body_size,
            "Average Weekly Range (pips)": weekly_range,
            "Average Weekly Body Size (pips)": weekly_body_size,
            "Average Asia Range": 0,  # TODO: Implement
            "Average Frankfurt Range": 0,  # TODO: Implement
            "Average London Range": 0,  # TODO: Implement
            "Average Lunch Range": 0,  # TODO: Implement
            "Average NY Range": 0,  # TODO: Implement
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
