from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class BaseMetric(ABC):
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir

    def load_timeframe_data(
        self, symbol: str, year: str, timeframe: str
    ) -> pd.DataFrame:
        """Load data for specific timeframe"""
        file_path = (
            self.timeframes_dir / symbol.lower() / f"{symbol}_{timeframe}_{year}.csv"
        )
        if not file_path.exists():
            raise FileNotFoundError(
                f"No data file found for {symbol} {timeframe} {year}"
            )

        df = pd.read_csv(
            file_path, parse_dates=["Date Time"] if timeframe != "1w" else None
        )
        if timeframe != "1w":
            df.set_index("Date Time", inplace=True)
        return df

    @abstractmethod
    def calculate(self, symbol: str, year: str) -> dict:
        """Calculate metric values"""
        pass
