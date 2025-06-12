from pathlib import Path
import pandas as pd  # type: ignore
from config.timeframes_config import TIMEFRAMES, TIMEFRAME_MAP


def create_timeframes_csv(
    input_path: Path, timeframes_dir: Path, symbol: str
) -> list[Path]:
    """
    Create OHLC data for different timeframes from input CSV file.
    Returns list of paths to created timeframe files.

    Args:
        input_path: Path to the input formatted CSV file
        timeframes_dir: Directory to save timeframe files
        symbol: Symbol name

    Returns:
        List of paths to created timeframe files
    """
    # Extract year from input file name
    try:
        year = input_path.stem.split("_")[-1]
    except (ValueError, IndexError):
        print(f"❌ Could not extract year from input file name: {input_path}")
        return []

    try:
        timeframes_dir.mkdir(parents=True, exist_ok=True)
        created_files = []

        # Create symbol directory once
        symbol_dir = timeframes_dir / symbol.lower()
        symbol_dir.mkdir(parents=True, exist_ok=True)

        # Check which files need to be created
        files_to_create = []
        for tf in TIMEFRAMES:
            output_file = symbol_dir / f"{symbol}_{tf}_{year}.csv"
            if output_file.exists():
                print(f"ℹ️ Timeframe file already exists: {output_file}")
                created_files.append(output_file)
            else:
                files_to_create.append((tf, output_file))

        # If no files need to be created, return early
        if not files_to_create:
            return created_files

        # Load the input CSV file only once for all timeframes
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

            # Create resampled data based on timeframe
            resampled = _create_timeframe_data(df, tf)

            if resampled is not None:
                _save_timeframe_data(resampled, output_file, tf, symbol, year)
                created_files.append(output_file)

        return created_files

    except Exception as e:
        print(f"❌ Error creating timeframes: {e}")
        return []


def _create_timeframe_data(df: pd.DataFrame, tf: str) -> pd.DataFrame | None:
    """Create resampled data for a specific timeframe."""
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
    """Create weekly timeframe data with proper Forex week alignment."""
    df_sorted = df.sort_index()
    start_date = df_sorted.index[0].normalize()

    # Align to Forex week (starts at Sunday 21:00 UTC)
    if start_date.weekday() != 0:
        days_to_next_monday = (7 - start_date.weekday()) % 7
        start_date = start_date + pd.Timedelta(days=days_to_next_monday)
        start_date = start_date + pd.Timedelta(hours=21)
        df_filtered = df_sorted[df_sorted.index >= start_date]
    else:
        df_filtered = df_sorted

    df_adjusted = df_filtered.copy()
    df_adjusted.index = df_adjusted.index - pd.Timedelta(hours=21)

    resampled = (
        df_adjusted.resample(
            TIMEFRAME_MAP[tf],
            origin="start",
            closed="left",
            label="left",
        )
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
        )
        .dropna()
    )

    # Filter weeks with at least 5 days of data
    resampled = resampled[
        resampled.index.map(
            lambda x: len(
                df_filtered[
                    (df_filtered.index >= x + pd.Timedelta(hours=21))
                    & (df_filtered.index < x + pd.Timedelta(days=7, hours=21))
                ]
            )
            >= 5
        )
    ]

    # Format weekly index
    resampled.index = resampled.index.map(
        lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=6)).strftime('%Y-%m-%d')}"
    )

    return resampled


def _create_daily_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Create daily timeframe data with Forex day alignment."""
    df_adjusted = df.copy()
    df_adjusted.index = df_adjusted.index - pd.Timedelta(hours=21)

    resampled = (
        df_adjusted.resample(
            TIMEFRAME_MAP[tf],
            origin="start",
            closed="left",
            label="left",
        )
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
        )
        .dropna()
    )

    resampled.index = pd.to_datetime(resampled.index.date)
    return resampled


def _create_intraday_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Create intraday timeframe data."""
    resampled = (
        df.resample(
            TIMEFRAME_MAP[tf],
            origin="start",
            offset="1min",
            closed="left",
            label="left",
        )
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
        )
        .dropna()
    )

    return resampled


def _save_timeframe_data(
    resampled: pd.DataFrame, output_file: Path, tf: str, symbol: str, year: str
) -> None:
    """Save timeframe data to CSV file."""
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
