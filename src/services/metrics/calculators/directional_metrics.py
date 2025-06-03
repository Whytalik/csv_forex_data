import pandas as pd  # type: ignore
from ..base_metric import BaseMetric
from .session_distribution_metrics import SessionDistributionMetrics


class DirectionalMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        # Create SessionDistributionMetrics instance to access cached data
        session_dist = SessionDistributionMetrics(self.timeframes_dir)

        # Get cached daily session data
        intermediate_cache_file = (
            session_dist.cache_dir / f"{symbol}_{year}_daily_session_data.csv"
        )

        if intermediate_cache_file.exists():
            try:
                daily_session_df = pd.read_csv(
                    intermediate_cache_file, parse_dates=["trading_date"]
                )
                # Use the new method to calculate directional metrics
                return session_dist.get_directional_metrics(daily_session_df)
            except Exception as e:
                print(f"Error loading cached data: {e}")

        # Fallback to empty metrics if no cached data
        metrics = {
            "Bullish Frankfurt-Asia Low %": 0,
            "Bullish London-Asia Low %": 0,
            "Bullish London-Frankfurt Low %": 0,
            "Bullish Lunch-Asia Low %": 0,
            "Bullish Lunch-London Low %": 0,
            "Bullish Lunch-Frankfurt Low %": 0,
            "Bullish NY-Asia Low %": 0,
            "Bullish NY-Frankfurt Low %": 0,
            "Bullish NY-London Low %": 0,
            "Bullish NY-Lunch Low %": 0,
            "Bearish Frankfurt-Asia High %": 0,
            "Bearish London-Asia High %": 0,
            "Bearish London-Frankfurt High %": 0,
            "Bearish Lunch-Asia High %": 0,
            "Bearish Lunch-Frankfurt High %": 0,
            "Bearish Lunch-London High %": 0,
            "Bearish NY-Asia High %": 0,
            "Bearish NY-Frankfurt High %": 0,
            "Bearish NY-London High %": 0,
            "Bearish NY-Lunch High %": 0,
        }

        return metrics
