import pandas as pd  # type: ignore
from ..base_metric import BaseMetric
from .session_distribution_metrics import SessionDistributionMetrics
from .directional_metrics import DirectionalMetrics


class IntradayMetrics(BaseMetric):
    def calculate(self, symbol: str, year: str) -> dict:
        session_dist = SessionDistributionMetrics(self.timeframes_dir)
        directional = DirectionalMetrics(self.timeframes_dir)

        intermediate_cache_file = (
            session_dist.cache_dir / f"{symbol}_{year}_daily_session_data.csv"
        )

        metrics = self._get_default_metrics(self._get_metric_names())

        if intermediate_cache_file.exists():
            try:
                daily_session_df = pd.read_csv(
                    intermediate_cache_file, parse_dates=["trading_date"]
                )

                # Get standard session comparison metrics
                session_metrics = session_dist.get_session_comparison_metrics(
                    daily_session_df
                )
                metrics.update(session_metrics)

                # Get directional (bullish/bearish) session interactions metrics
                directional_metrics = directional.calculate(symbol, year)
                metrics.update(directional_metrics)

                # Get bullish/bearish session distribution metrics
                directional_session_metrics = (
                    session_dist.get_directional_session_distribution(daily_session_df)
                )
                metrics.update(directional_session_metrics)

            except Exception as e:
                print(f"Error loading cached data: {e}")

        return metrics

    def _get_metric_names(self) -> list[str]:
        return [
            "Frankfurt-Asia High %",
            "Frankfurt-Asia Low %",
            "London-Asia High %",
            "London-Asia Low %",
            "London-Frankfurt High %",
            "London-Frankfurt Low %",
            "Lunch-Asia High %",
            "Lunch-Asia Low %",
            "Lunch-London High %",
            "Lunch-London Low %",
            "Lunch-Frankfurt High %",
            "Lunch-Frankfurt Low %",
            "NY-Asia High %",
            "NY-Asia Low %",
            "NY-Frankfurt High %",
            "NY-Frankfurt Low %",
            "NY-London High %",
            "NY-London Low %",
            "NY-Lunch High %",
            "NY-Lunch Low %",
        ]
