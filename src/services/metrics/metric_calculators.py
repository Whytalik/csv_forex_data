from pathlib import Path
import pandas as pd
from .base_metric import BaseMetric
from config.sessions_config import SESSIONS


class VolatilityMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes
        daily_data = self.load_timeframe_data(symbol, year, "1d")
        weekly_data = self.load_timeframe_data(symbol, year, "1w")

        metrics = {
            "Average Daily Range (pips)": 0,  # TODO: Implement
            "Average Daily Body Size (pips)": 0,  # TODO: Implement
            "Average Weekly Range (pips)": 0,  # TODO: Implement
            "Average Weekly Body Size (pips)": 0,  # TODO: Implement
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
        m1_data = self.load_timeframe_data(symbol, year, "1m")

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
        m1_data = self.load_timeframe_data(symbol, year, "1m")

        metrics = {
            "Frankfurt-Asia High %": 0,  # TODO: Implement
            "Frankfurt-Asia Low %": 0,  # TODO: Implement
            # ... Add all other intraday metrics
        }

        return metrics


class DirectionalMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Load required timeframes
        m1_data = self.load_timeframe_data(symbol, year, "1m")

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
