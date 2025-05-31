from pathlib import Path
import pandas as pd
from datetime import datetime
from config.timeframes_config import TIMEFRAMES, TIMEFRAME_MAP


def collect_csv_files(directory: Path) -> list[Path]:
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        return []
    return list(directory.glob("*.csv"))


def merge_csv_files(
    csv_files: list[Path], output_dir: Path, prefix: str
) -> Path | None:
    """
    Merge CSV files into a single file if it doesn't exist yet.
    Returns the path to the merged file (either existing or newly created).
    """
    if not csv_files:
        print("No CSV files found to merge")
        return None

    years = []
    for file in csv_files:
        try:
            year_str = file.stem.split("_")[-1]
            years.append(int(year_str))
        except (ValueError, IndexError) as e:
            print(f"Error extracting year from {file}: {e}")
            continue

    if not years:
        print("No valid years found in filenames")
        return None

    latest_year = max(years)
    output_file = output_dir / f"{prefix}_merged_{latest_year}.csv"

    if output_file.exists():
        print(f"ℹ️ Merged file already exists: {output_file}")
        return output_file

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(
                file,
                sep=";",
                header=None,
                names=["datetime", "open", "high", "low", "close", "volume"],
            )
            df = df.drop(columns=["volume"])
            dfs.append(df)
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            continue

    if not dfs:
        print("No valid data to merge")
        return None

    try:
        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df.sort_values("datetime", inplace=True)
        merged_df.to_csv(output_file, sep=";", index=False, header=False)
        print(f"✅ Merged data saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error saving merged file: {e}")
        return None


def reformat_data(input_path: Path, output_file: Path) -> Path | None:
    """
    Reformat data from merged CSV file.
    Returns the path to the reformatted file (either existing or newly created).
    """
    if output_file.exists():
        print(f"ℹ️ Reformatted file already exists: {output_file}")
        return output_file

    try:
        df = pd.read_csv(
            input_path,
            sep=";",
            header=None,
            names=["datetime", "open", "high", "low", "close"],
        )

        df["datetime"] = df["datetime"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d %H%M%S").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        df.to_csv(
            output_file,
            sep=",",
            index=False,
            header=["Date Time", "Open", "High", "Low", "Close"],
        )
        print(f"✅ Reformatted data saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error reformatting data: {e}")
        return None


def create_timeframes_csv(
    input_path: Path, timeframes_dir: Path, symbol: str, year: str
) -> list[Path]:
    """
    Create OHLC data for different timeframes from input CSV file.
    Returns list of paths to created timeframe files.
    """
    try:
        timeframes_dir.mkdir(parents=True, exist_ok=True)
        created_files = []

        for tf in TIMEFRAMES:
            # Create symbol directory if it doesn't exist
            symbol_dir = timeframes_dir / symbol.lower()
            symbol_dir.mkdir(parents=True, exist_ok=True)

            # Check if file already exists
            output_file = symbol_dir / f"{symbol}_{tf}_{year}.csv"
            if output_file.exists():
                print(f"ℹ️ Timeframe file already exists: {output_file}")
                created_files.append(output_file)
                continue

            if tf not in TIMEFRAME_MAP:
                print(f"Unsupported timeframe: {tf}")
                continue

            # Read the input CSV file only if we need to create at least one new file
            if not "df" in locals():
                df = pd.read_csv(
                    input_path,
                    sep=",",
                    parse_dates=["Date Time"],
                )
                # Rename columns to lowercase for consistency
                df = df.rename(
                    columns={
                        "Date Time": "datetime",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                    }
                )
                df.set_index(
                    "datetime", inplace=True
                )  # Resample data according to timeframe            if tf == "1w":
                # Ensure we start with Monday 21:00 for weekly data
                df = df.sort_index()
                start_date = df.index[0].normalize()
                if start_date.weekday() != 0:  # If not Monday
                    # Find next Monday
                    days_to_next_monday = (7 - start_date.weekday()) % 7
                    start_date = start_date + pd.Timedelta(days=days_to_next_monday)
                    # Add 21 hours to start at 21:00
                    start_date = start_date + pd.Timedelta(hours=21)
                    df = df[df.index >= start_date]# Resample data
            if tf in ["1d", "1w"]:
                # Adjust index for daily/weekly data to start at 21:00
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
                # Adjust index back
                resampled.index = resampled.index + pd.Timedelta(hours=21)
            else:
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

            if tf == "1w":
                resampled = resampled[
                    resampled.index.map(
                        lambda x: len(
                            df[(df.index >= x) & (df.index < x + pd.Timedelta(days=7))]
                        )
                        >= 5
                    )
                ]

            if tf == "1w":
                resampled.index = resampled.index.map(
                    lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=6)).strftime('%Y-%m-%d')}"
                )  # Save to CSV with increased precision
            resampled.to_csv(
                output_file,
                sep=",",
                index=True,
                header=["Open", "High", "Low", "Close"],
                date_format="%Y-%m-%d %H:%M:%S" if tf != "1w" else None,
                float_format="%.5f",  # Збільшуємо точність до 5 знаків після коми
            )

            print(f"✅ Created {tf} timeframe data for {symbol} ({year})")
            created_files.append(output_file)

        return created_files

    except Exception as e:
        print(f"❌ Error creating timeframes: {e}")
        return []
