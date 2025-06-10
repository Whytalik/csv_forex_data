from pathlib import Path
import pandas as pd  # type: ignore
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
            lambda x: (
                datetime.strptime(str(x), "%Y%m%d %H%M%S") + pd.Timedelta(days=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
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
    input_path: Path, timeframes_dir: Path, symbol: str
) -> list[Path]:
    """
    Create OHLC data for different timeframes from input CSV file.
    Returns list of paths to created timeframe files.
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
            if tf == "1w":
                df_sorted = df.sort_index()
                start_date = df_sorted.index[0].normalize()
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
                                & (
                                    df_filtered.index
                                    < x + pd.Timedelta(days=7, hours=21)
                                )
                            ]
                        )
                        >= 5
                    )
                ]

                # Format weekly index
                resampled.index = resampled.index.map(
                    lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=6)).strftime('%Y-%m-%d')}"
                )

            elif tf == "1d":
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
            created_files.append(output_file)

        return created_files

    except Exception as e:
        files_to_create = []
        for tf in TIMEFRAMES:
            output_file = symbol_dir / f"{symbol}_{tf}_{year}.csv"
            if output_file.exists():
                print(f"ℹ️ Timeframe file already exists: {output_file}")
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

            if tf == "1w":
                df_sorted = df.sort_index()
                start_date = df_sorted.index[0].normalize()
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

                resampled = resampled[
                    resampled.index.map(
                        lambda x: len(
                            df_filtered[
                                (df_filtered.index >= x + pd.Timedelta(hours=21))
                                & (
                                    df_filtered.index
                                    < x + pd.Timedelta(days=7, hours=21)
                                )
                            ]
                        )
                        >= 5
                    )
                ]

                resampled.index = resampled.index.map(
                    lambda x: f"{x.strftime('%Y-%m-%d')} to {(x + pd.Timedelta(days=6)).strftime('%Y-%m-%d')}"
                )

            elif tf == "1d":
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
            created_files.append(output_file)

        return created_files

    except Exception as e:
        print(f"❌ Error creating timeframes: {e}")
        return []
