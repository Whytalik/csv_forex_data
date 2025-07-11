from pathlib import Path
from typing import Dict, Any
from .calculators.volatility_metrics import VolatilityMetrics
from .calculators.session_distribution_metrics import SessionDistributionMetrics
from .calculators.intraday_metrics import IntradayMetrics
from .calculators.occurrence_metrics import OccurrenceMetrics
from .calculators.levels_metrics import LevelsMetrics


class MetricsManager:
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir
        self.calculators = {
            "Volatility & Range Metrics": VolatilityMetrics(timeframes_dir),
            "High/Low Timing Distribution (per Session)": SessionDistributionMetrics(
                timeframes_dir
            ),
            "Intraday Interval High/Low Percentages": IntradayMetrics(timeframes_dir),
            "Daily/Weekly Occurrence Statistics": OccurrenceMetrics(timeframes_dir),
            "Key Levels": LevelsMetrics(timeframes_dir),
        }

    def calculate_all_metrics(self, symbol: str, year: str) -> Dict[str, Any]:
        """Calculate all metrics for a given symbol and year"""
        all_metrics = {}

        for name, calculator in self.calculators.items():
            metrics = calculator.calculate(symbol, year)
            all_metrics.update(metrics)

        return all_metrics

    def calculate_specific_metrics(
        self, symbol: str, year: str, metric_groups: list[str]
    ) -> Dict[str, Any]:
        """Calculate specific metric groups for a given symbol and year"""
        specific_metrics = {}

        for group in metric_groups:
            if group in self.calculators:
                metrics = self.calculators[group].calculate(symbol, year)
                specific_metrics.update(metrics)

        return specific_metrics
