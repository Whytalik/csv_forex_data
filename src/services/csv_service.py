from pathlib import Path
import pandas as pd
from datetime import datetime


def collect_csv_files(directory: Path) -> list[Path]:
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        return []
    return list(directory.glob("*.csv"))


def merge_csv_files(csv_files: list[Path], output_file: Path) -> None:
    if not csv_files:
        print("No CSV files found to merge")
        return

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(
                file,
                sep=";",
                header=None,
                names=["datetime", "open", "high", "low", "close", "volume"],
            )
            dfs.append(df)
        except Exception as e:
            print(f"Error reading file {file}: {e}")

    if not dfs:
        print("No valid data to merge")
        return

    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.sort_values("datetime", inplace=True)

    try:
        merged_df.to_csv(output_file, sep=";", index=False, header=False)
        print(f"Merged data saved to {output_file}")
    except Exception as e:
        print(f"Error saving merged file: {e}")

    return merged_df


def reformat_data(df: pd.DataFrame, output_file: Path) -> None:
    """Reformat merged data to more readable format"""
    try:
        df["datetime"] = df["datetime"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d %H%M%S").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        df.to_csv(
            output_file,
            sep=",",
            index=False,
            header=["Date Time", "Open", "High", "Low", "Close", "Volume"],
        )
        print(f"Reformatted data saved to {output_file}")
    except Exception as e:
        print(f"Error reformatting data: {e}")
