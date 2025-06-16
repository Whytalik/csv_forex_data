from pathlib import Path
import pandas as pd  # type: ignore
from config.timeframes_config import TIMEFRAMES, TIMEFRAME_MAP


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
    """Create weekly timeframe data with proper Forex week alignment."""
    df_sorted = df.sort_index()
    start_date = df_sorted.index[0].normalize()

    # Align to Forex week
    if start_date.weekday() != 0:
        days_to_next_monday = (7 - start_date.weekday()) % 7
        start_date = start_date + pd.Timedelta(days=days_to_next_monday)
        df_filtered = df_sorted[df_sorted.index >= start_date]
    else:
        df_filtered = df_sorted

    resampled = (
        df_filtered.resample(
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
                    (df_filtered.index >= x)
                    & (df_filtered.index < x + pd.Timedelta(days=7))
                ]
            )
            >= 5
        )
    ]

    # Format weekly index
    resampled.index = resampled.index.map(
        lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=5)).strftime('%Y-%m-%d')}"
    )

    return resampled


def _create_daily_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Create daily timeframe data with proper forex market days (exclude weekends)."""
    resampled = (
        df.resample(
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

    resampled = resampled[resampled.index.weekday < 5]

    return resampled


def _create_intraday_data(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Create intraday timeframe data with proper time alignment."""
    # Спочатку перетворюємо індекс в datetime, якщо він ще не такий
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Визначаємо параметри ресемплінгу
    resampled = (
        df.resample(
            TIMEFRAME_MAP[tf],
            origin="start_day",  # Використовуємо початок дня як точку відліку
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

    # Створюємо новий DataFrame з вирівняними даними
    if tf in ["1h", "4h"]:
        # Створюємо нові часові мітки, вирівняні по годинах
        aligned_times = []
        aligned_data = []

        for timestamp, row in resampled.iterrows():
            # Округляємо час до найближчої години кратної інтервалу
            if tf == "1h":
                new_time = timestamp.replace(minute=0, second=0, microsecond=0)
            elif tf == "4h":
                # Для 4h: округляємо до 00, 04, 08, 12, 16, 20
                hour = (timestamp.hour // 4) * 4
                new_time = timestamp.replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )

            aligned_times.append(new_time)
            aligned_data.append(row.values)

        # Створюємо новий DataFrame з вирівняними часовими мітками
        aligned_df = pd.DataFrame(
            aligned_data, index=aligned_times, columns=resampled.columns
        )
        return aligned_df

    elif tf == "15m":
        # Для 15-хвилинного таймфрейму - вирівнювання на 00, 15, 30, 45 хвилин
        aligned_index = resampled.index.map(
            lambda x: x.replace(minute=(x.minute // 15) * 15, second=0, microsecond=0)
        )
        resampled.index = aligned_index

    elif tf == "5m":
        # Для 5-хвилинного таймфрейму - вирівнювання на 00, 05, 10, ..., 55 хвилин
        aligned_index = resampled.index.map(
            lambda x: x.replace(minute=(x.minute // 5) * 5, second=0, microsecond=0)
        )
        resampled.index = aligned_index

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
