from pathlib import Path
from typing import Dict, Any
import pandas as pd
from ..base_metric import BaseMetric


class LevelsMetrics(BaseMetric):
    def __init__(self, timeframes_dir: Path):
        super().__init__(timeframes_dir)
        import logging

        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def calculate(self, symbol: str, year: str) -> Dict[str, Any]:
        try:
            daily_data = self._load_timeframe_data(symbol, year, "1d")
            if daily_data is None or daily_data.empty:
                return self._get_default_metrics()

            pdh_probability = self._calculate_pdh_probability(daily_data)

            pdl_probability = self._calculate_pdl_probability(daily_data)

            pd_levels_probability = self._calculate_pd_levels_probability(daily_data)

            return {
                "PDH Probability": pdh_probability,
                "PDL Probability": pdl_probability,
                "PD Levels Probability": pd_levels_probability,
            }

        except Exception as e:
            self.logger.error(
                f"Error calculating levels metrics for {symbol} {year}: {e}"
            )
            return self._get_default_metrics()

    def _calculate_pdh_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability of reaching Previous Day High."""
        if len(daily_data) < 2:
            return 0.0

        daily_data["prev_high"] = daily_data["High"].shift(1)

        reaches_pdh = daily_data["High"] >= daily_data["prev_high"]

        valid_days = reaches_pdh.dropna()
        if len(valid_days) == 0:
            return 0.0

        probability = (valid_days.sum() / len(valid_days)) * 100
        return round(probability, 2)

    def _calculate_pdl_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability of reaching Previous Day Low."""
        if len(daily_data) < 2:
            return 0.0

        daily_data["prev_low"] = daily_data["Low"].shift(1)

        reaches_pdl = daily_data["Low"] <= daily_data["prev_low"]

        valid_days = reaches_pdl.dropna()
        if len(valid_days) == 0:
            return 0.0

        probability = (valid_days.sum() / len(valid_days)) * 100
        return round(probability, 2)

    def _calculate_pd_levels_probability(self, daily_data: pd.DataFrame) -> float:
        """Calculate probability of reaching either Previous Day High OR Low."""
        if len(daily_data) < 2:
            return 0.0

        daily_data["prev_high"] = daily_data["High"].shift(1)
        daily_data["prev_low"] = daily_data["Low"].shift(1)

        reaches_pdh = daily_data["High"] >= daily_data["prev_high"]
        reaches_pdl = daily_data["Low"] <= daily_data["prev_low"]
        reaches_either = reaches_pdh | reaches_pdl

        valid_days = reaches_either.dropna()
        if len(valid_days) == 0:
            return 0.0
        probability = (valid_days.sum() / len(valid_days)) * 100
        return round(probability, 2)

    def _get_metric_names(self) -> list[str]:
        return ["PDH Probability", "PDL Probability", "PD Levels Probability"]

    def _get_default_metrics(self) -> Dict[str, Any]:
        return super()._get_default_metrics(self._get_metric_names())
