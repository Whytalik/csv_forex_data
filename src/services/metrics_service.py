from pathlib import Path
from typing import Dict, Any
from config.metrics import get_metrics_for_profile
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
        return self.metrics_manager.calculate_all_metrics(symbol, year)

    def calculate_metrics_for_profile(self, symbol: str, profile: str) -> Dict[str, Dict[str, Any]]:
        """Calculate metrics for a specific profile"""
        year = self._extract_year_from_file(symbol)
        all_metrics = self.metrics_manager.calculate_all_metrics(symbol, year)
        
        # Get profile-specific metrics configuration
        profile_metrics = get_metrics_for_profile(profile)
        
        # Filter metrics based on profile configuration
        grouped_metrics = {}
        for category, metrics_list in profile_metrics.items():
            category_metrics = {
                key: value for key, value in all_metrics.items() if key in metrics_list
            }
            if category_metrics:
                grouped_metrics[category] = category_metrics
        
        return grouped_metrics
