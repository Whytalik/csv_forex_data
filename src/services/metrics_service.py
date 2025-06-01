from pathlib import Path
from typing import Dict, Any
from config.metrics import BASE_METRICS
from services.metrics.metrics_manager import MetricsManager


class MetricsService:
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir
        self.metrics_manager = MetricsManager(timeframes_dir)

    def _extract_year_from_file(self, symbol: str) -> str:
        """Extract year from timeframe file"""
        pattern = f"{symbol}_1d_*.csv"
        symbol_dir = self.timeframes_dir / symbol.lower()
        matches = list(symbol_dir.glob(pattern))
        if not matches:
            raise FileNotFoundError(f"No data files found matching pattern: {pattern}")
        return matches[0].stem.split("_")[-1]

    def calculate_all_metrics(self, symbol: str) -> Dict[str, Dict[str, Any]]:
        """Calculate all available metrics for a symbol"""
        year = self._extract_year_from_file(symbol)
        all_metrics = self.metrics_manager.calculate_all_metrics(symbol, year)

        grouped_metrics = {}
        for group, metrics_list in BASE_METRICS.items():
            group_metrics = {
                key: value for key, value in all_metrics.items() if key in metrics_list
            }
            if group_metrics:
                grouped_metrics[group] = group_metrics

        if "Date Range" in all_metrics:
            grouped_metrics["Aggregated / Thematic Metrics"] = {
                "Date Range": all_metrics["Date Range"]
            }

        return grouped_metrics
