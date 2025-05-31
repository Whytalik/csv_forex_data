from datetime import datetime, time
from pathlib import Path
from typing import Dict
import pandas as pd
from config.sessions_config import SESSIONS


def _parse_time(time_str: str) -> time:
    """Convert time string in format HH:MM to time object"""
    return datetime.strptime(time_str, "%H:%M").time()


class MetricsService:
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir
        self.sessions = {
            session: (_parse_time(times["start"]), _parse_time(times["end"]))
            for session, times in SESSIONS.items()
        }
        
    def _load_timeframe_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Load data for specific timeframe"""
        pattern = f"{symbol}_{timeframe}_*.csv"
        symbol_dir = self.timeframes_dir / symbol.lower()
        matches = list(symbol_dir.glob(pattern))

        if not matches:
            raise FileNotFoundError(f"No data files found matching pattern: {pattern}")
        if len(matches) > 1:
            raise ValueError(
                f"Expected one file for pattern {pattern}, but found multiple: {matches}"
            )
        
        # Read CSV file
        if timeframe == "1w":
            # For weekly data, read without parsing dates first
            df = pd.read_csv(matches[0])
            # Extract start date from the range (e.g., "2000-06-05 to 2000-06-11" -> "2000-06-05")
            df["Date Time"] = df["Date Time"].str.split(" to").str[0]
            # Now parse the extracted date
            df["Date Time"] = pd.to_datetime(df["Date Time"])
        else:
            # For other timeframes, parse dates directly
            df = pd.read_csv(matches[0])
            df["Date Time"] = pd.to_datetime(df["Date Time"])
        
        return df

    def calculate_volatility_metrics(self, symbol: str) -> Dict[str, float]:
        """Calculate volatility and range metrics"""
        daily_data = self._load_timeframe_data(symbol, "1d")
        weekly_data = self._load_timeframe_data(symbol, "1w")
        hourly_data = self._load_timeframe_data(symbol, "1h")

        metrics = {
            "Average Daily Range (pips)": 0.0,
            "Average Daily Body Size (pips)": 0.0,
            "Average Weekly Range (pips)": 0.0,
            "Average Weekly Body Size (pips)": 0.0,
            "Average Asia Range": 0.0,
            "Average Frankfurt Range": 0.0,
            "Average London Range": 0.0,
            "Average Lunch Range": 0.0,
            "Average NY Range": 0.0,
        }
        return metrics

    def calculate_session_distribution(self, symbol: str) -> Dict[str, float]:
        """Calculate high/low distribution per session"""
        hourly_data = self._load_timeframe_data(symbol, "1h")

        metrics = {
            "Daily High in Asia %": 0.0,
            "Daily High in Frankfurt %": 0.0,
            "Daily High in London %": 0.0,
            "Daily High in Lunch %": 0.0,
            "Daily High in NY %": 0.0,
            "Daily High in Out of Session %": 0.0,
            "Daily Low in Asia %": 0.0,
            "Daily Low in Frankfurt %": 0.0,
            "Daily Low in London %": 0.0,
            "Daily Low in NY %": 0.0,
            "Daily Low in Lunch %": 0.0,
            "Daily Low in Out of Session %": 0.0,
        }
        return metrics

    def calculate_intraday_metrics(self, symbol: str) -> Dict[str, float]:
        """Calculate intraday interval high/low percentages"""
        hourly_data = self._load_timeframe_data(symbol, "1h")

        metrics = {
            "Frankfurt-Asia High %": 0.0,
            "Frankfurt-Asia Low %": 0.0,
            # ... (other metrics in this group)
        }
        return metrics

    def calculate_directional_metrics(self, symbol: str) -> Dict[str, float]:
        """Calculate bullish/bearish specific metrics"""
        hourly_data = self._load_timeframe_data(symbol, "1h")

        metrics = {
            "Bullish Frankfurt-Asia Low %": 0.0,
            "Bullish London-Asia Low %": 0.0,
            # ... (other metrics in this group)
        }
        return metrics

    def calculate_occurrence_stats(self, symbol: str) -> Dict[str, float]:
        """Calculate daily/weekly occurrence statistics"""
        daily_data = self._load_timeframe_data(symbol, "1d")

        metrics = {
            "High in Monday": 0.0,
            "High in Tuesday": 0.0,
            # ... (other metrics in this group)
        }
        return metrics

    def calculate_all_metrics(self, symbol: str) -> Dict[str, Dict[str, float]]:
        """Calculate all metrics for a symbol"""
        # Get date range from the data
        daily_data = self._load_timeframe_data(symbol, "1d")
        date_range = f"{daily_data['Date Time'].min():%Y-%m-%d} to {daily_data['Date Time'].max():%Y-%m-%d}"

        return {
            "Volatility & Range Metrics": self.calculate_volatility_metrics(symbol),
            "High/Low Timing Distribution (per Session)": self.calculate_session_distribution(
                symbol
            ),
            "Intraday Interval High/Low Percentages": self.calculate_intraday_metrics(
                symbol
            ),
            "Bullish / Bearish Specific Metrics": self.calculate_directional_metrics(
                symbol
            ),
            "Daily/Weekly Occurrence Statistics": self.calculate_occurrence_stats(
                symbol
            ),
            "Aggregated / Thematic Metrics": {"Date Range": date_range},
        }
