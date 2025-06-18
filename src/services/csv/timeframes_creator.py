from pathlib import Path
import pandas as pd  # type: ignore
from config.timeframes_config import TIMEFRAMES, TIMEFRAME_MAP
from utils.datetime_utils import (
    determine_day_start_hour,
    get_forex_week_start,
    get_forex_trading_date,
)


def create_timeframes_csv(
    input_path: Path, timeframes_dir: Path, symbol: str
) -> list[Path]:
    try:
        year = input_path.stem.split("_")[-1]
    except (ValueError, IndexError):
        print(f"❌ Could not extract year from input file name: {input_path}")
        return []

    try:
        timeframes_dir.mkdir(parents=True, exist_ok=True)
        created_files = []

        symbol_dir = timeframes_dir / symbol.lower()
        symbol_dir.mkdir(parents=True, exist_ok=True)

        files_to_create = []
        for tf in TIMEFRAMES:
            output_file = symbol_dir / f"{symbol}_{tf}_{year}.csv"
            if output_file.exists():
                print(f"ℹ️ Timeframe file already exists: {output_file.name}")
                created_files.append(output_file)
            else:
                files_to_create.append((tf, output_file))

        if not files_to_create:
            return created_files

        print(f"📊 Loading data for {symbol} timeframe processing...")
        df = pd.read_csv(input_path, sep=",", parse_dates=["Date Time"])
        df = df.rename(
            columns={
                "Date Time": "Date Time",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
            }
        )
        df.set_index("Date Time", inplace=True)

        for tf, output_file in files_to_create:
            if tf not in TIMEFRAME_MAP:
                print(f"Unsupported timeframe: {tf}")
                continue

            resampled = _create_timeframe_data(df, tf)

            if resampled is not None:
                _save_timeframe_data(resampled, output_file, tf, symbol, year)
                created_files.append(output_file)

        return created_files

    except Exception as e:
        print(f"❌ Error creating timeframes: {e}")
        return []


def _create_timeframe_data(df: pd.DataFrame, tf: str) -> pd.DataFrame | None:
    try:
        if tf == "1w":
            return _create_weekly_data(df, tf)
        elif tf == "1d":
            return _create_daily_data(df, tf)
        else:
            return _create_intraday_data(df, tf)
    except Exception as e:
        print(f"❌ Error creating {tf} timeframe data: {e}")
        return None


def _create_weekly_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    print("📊 Creating weekly timeframe data with weeks starting on Monday...")

    df_copy = df.copy()

    df_copy["trading_date"] = df_copy.index.map(get_forex_trading_date)

    df_copy["week_start"] = df_copy["trading_date"].map(
        lambda x: x - pd.Timedelta(days=x.weekday())
    )

    resampled = df_copy.groupby("week_start").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )

    resampled.index = resampled.index.map(
        lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=4)).strftime('%Y-%m-%d')}"
    )

    print(f"✅ Weekly candles created: {len(resampled)} weeks")
    return resampled


def _create_daily_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    print("📊 Creating daily timeframe data...")
    df_copy = df.copy()
    df_copy["trading_date"] = df_copy.index.map(get_forex_trading_date)

    resampled = df_copy.groupby("trading_date").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )

    resampled = resampled[resampled.index.map(lambda x: pd.Timestamp(x).weekday() < 5)]

    print(f"✅ Daily candles created: {len(resampled)} trading days")
    return resampled


def _create_intraday_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    print(f"📊 Creating {tf} timeframe data...")

    df_copy = df.copy()
    df_copy["trading_date"] = df_copy.index.map(get_forex_trading_date)
    df_filtered = df_copy[
        df_copy["trading_date"].map(lambda x: pd.Timestamp(x).weekday() < 5)
    ]

    df_filtered = df_filtered.drop("trading_date", axis=1)

    resampled = (
        df_filtered.resample(TIMEFRAME_MAP[tf], closed="left", label="left")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
    )

    if tf == "1h" or tf == "4h":
        resampled.index = resampled.index.map(
            lambda x: x.replace(minute=0, second=0, microsecond=0)
        )
    elif tf == "15m":
        resampled.index = resampled.index.map(
            lambda x: x.replace(minute=(x.minute // 15) * 15, second=0, microsecond=0)
        )
    elif tf == "5m":
        resampled.index = resampled.index.map(
            lambda x: x.replace(minute=(x.minute // 5) * 5, second=0, microsecond=0)
        )

    print(f"✅ {tf} candles created: {len(resampled)} bars")
    return resampled


def _save_timeframe_data(
    resampled: pd.DataFrame, output_file: Path, tf: str, symbol: str, year: str
) -> None:
    try:
        resampled.to_csv(
            output_file,
            sep=",",
            index=True,
            header=["Open", "High", "Low", "Close"],
            date_format=(
                "%Y-%m-%d"
                if tf == "1d"
                else ("%Y-%m-%d %H:%M:%S" if tf != "1w" else None)
            ),
            float_format="%.5f",
        )
        print(f"✅ Created {tf} timeframe data for {symbol} ({year})")
    except Exception as e:
        print(f"❌ Error saving {tf} timeframe data: {e}")
        raise
