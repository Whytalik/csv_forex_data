from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd # type: ignore


class BaseMetric(ABC):    
    def __init__(self, timeframes_dir: Path):
        self.timeframes_dir = timeframes_dir
    def filter_anomalies(
        self, df: pd.DataFrame, columns: list[str], n_std: float = 3
    ) -> pd.DataFrame:
        """
        Filter out anomalies using standard deviation method
        :param df: DataFrame to filter
        :param columns: List of columns to check for anomalies
        :param n_std: Number of standard deviations to use as threshold (default 3)
        :return: Filtered DataFrame
        """
        filtered_data = df.copy()
        combined_mask = pd.Series(True, index=df.index)

        for column in columns:
            mean = df[column].mean()
            std = df[column].std()
            column_mask = (df[column] >= mean - n_std * std) & (df[column] <= mean + n_std * std)
            combined_mask &= column_mask

        filtered_data = filtered_data[combined_mask]
        return filtered_data

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

        std_threshold = 5 if timeframe == "1w" else 3
        df = self.filter_anomalies(df, ["Open", "High", "Low", "Close"], std_threshold)
        
        if timeframe != "1w":
            df.set_index("Date Time", inplace=True)

        return df

    @abstractmethod
    def calculate(self, symbol: str, year: str) -> dict:
        """Calculate metric values"""
        pass
