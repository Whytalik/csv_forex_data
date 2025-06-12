from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd  # type: ignore
from functools import lru_cache


class BaseMetric(ABC):
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir
        self._data_cache = {}

    @lru_cache(maxsize=128)
    def filter_anomalies(
        self, df_hash: int, columns_tuple: tuple, n_std: float = 3
    ) -> pd.DataFrame:
        pass

    def _filter_anomalies_internal(
        self, df: pd.DataFrame, columns: list[str], n_std: float = 3
    ) -> pd.DataFrame:
        """
        Internal method to filter out anomalies
        """
        filtered_data = df.copy()
        combined_mask = pd.Series(True, index=df.index)

        for column in columns:
            if column in df.columns:
                mean = df[column].mean()
                std = df[column].std()
                column_mask = (df[column] >= mean - n_std * std) & (
                    df[column] <= mean + n_std * std
                )
                combined_mask &= column_mask

        filtered_data = filtered_data[combined_mask]
        return filtered_data

    def load_timeframe_data(
        self, symbol: str, year: str, timeframe: str
    ) -> pd.DataFrame:
        """Load data for specific timeframe with caching"""
        cache_key = f"{symbol}_{timeframe}_{year}"

        if cache_key in self._data_cache:
            return self._data_cache[cache_key].copy()

        file_path = (
            self.timeframes_dir / symbol.lower() / f"{symbol}_{timeframe}_{year}.csv"
        )
        if not file_path.exists():
            raise FileNotFoundError(
                f"No data file found for {symbol} {timeframe} {year}"
            )

        df = pd.read_csv(
            file_path,
            index_col=0,
            parse_dates=True if timeframe != "1w" else False,
            dtype={
                "Open": "float32",
                "High": "float32",
                "Low": "float32",
                "Close": "float32",
            },
        )

        std_threshold = 5 if timeframe == "1w" else 3
        df = self._filter_anomalies_internal(
            df, ["Open", "High", "Low", "Close"], std_threshold
        )
        if len(self._data_cache) < 50:
            self._data_cache[cache_key] = df.copy()

        return df

    def clear_cache(self):
        """Clear the data cache"""
        self._data_cache.clear()

    @staticmethod
    def round_metric(value: float, decimals: int = 2) -> float:
        """Round metric value to specified decimal places"""
        try:
            if value is None or (
                isinstance(value, float)
                and (value != value or value == float("inf") or value == float("-inf"))
            ):
                return 0.0
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return 0.0

    def _get_default_metrics(self, metric_names: list[str] = None) -> dict:
        if not metric_names:
            return {}

        return {metric_name: 0.0 for metric_name in metric_names}

    @abstractmethod
    def calculate(self, symbol: str, year: str) -> dict:
        """Calculate metric values"""
        pass
