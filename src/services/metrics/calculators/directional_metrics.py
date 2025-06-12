import pandas as pd  # type: ignore
from ..base_metric import BaseMetric
from .session_distribution_metrics import SessionDistributionMetrics


class DirectionalMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        session_dist = SessionDistributionMetrics(self.timeframes_dir)

        intermediate_cache_file = (
            session_dist.cache_dir / f"{symbol}_{year}_daily_session_data.csv"
        )

        if intermediate_cache_file.exists():
            try:
                daily_session_df = pd.read_csv(
                    intermediate_cache_file, parse_dates=["trading_date"]
                )
                return session_dist.get_directional_metrics(daily_session_df)
            except Exception as e:
                print(f"Error loading cached data: {e}")

        return self._get_default_metrics(self._get_metric_names())

    def _get_metric_names(self) -> list[str]:
        return [
            "Bullish Frankfurt-Asia Low %",
            "Bullish London-Asia Low %",
            "Bullish London-Frankfurt Low %",
            "Bullish Lunch-Asia Low %",
            "Bullish Lunch-London Low %",
            "Bullish Lunch-Frankfurt Low %",
            "Bullish NY-Asia Low %",
            "Bullish NY-Frankfurt Low %",
            "Bullish NY-London Low %",
            "Bullish NY-Lunch Low %",
            "Bearish Frankfurt-Asia High %",
            "Bearish London-Asia High %",
            "Bearish London-Frankfurt High %",
            "Bearish Lunch-Asia High %",
            "Bearish Lunch-Frankfurt High %",
            "Bearish Lunch-London High %",
            "Bearish NY-Asia High %",
            "Bearish NY-Frankfurt High %",
            "Bearish NY-London High %",
            "Bearish NY-Lunch High %",
        ]
