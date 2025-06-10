import pandas as pd  # type: ignore
from ..base_metric import BaseMetric
from .session_distribution_metrics import SessionDistributionMetrics


class IntradayMetrics(BaseMetric):
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
                return session_dist.get_session_comparison_metrics(daily_session_df)
            except Exception as e:
                print(f"Error loading cached data: {e}")

        metrics = {
            "Frankfurt-Asia High %": 0,
            "Frankfurt-Asia Low %": 0,
            "London-Asia High %": 0,
            "London-Asia Low %": 0,
            "London-Frankfurt High %": 0,
            "London-Frankfurt Low %": 0,
            "Lunch-Asia High %": 0,
            "Lunch-Asia Low %": 0,
            "Lunch-London High %": 0,
            "Lunch-London Low %": 0,
            "Lunch-Frankfurt High %": 0,
            "Lunch-Frankfurt Low %": 0,
            "NY-Asia High %": 0,
            "NY-Asia Low %": 0,
            "NY-Frankfurt High %": 0,
            "NY-Frankfurt Low %": 0,
            "NY-London High %": 0,
            "NY-London Low %": 0,
            "NY-Lunch High %": 0,
            "NY-Lunch Low %": 0,
        }

        return metrics
