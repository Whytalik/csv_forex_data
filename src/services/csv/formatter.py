from pathlib import Path
import pandas as pd  # type: ignore
from datetime import datetime


def reformat_data(input_path: Path, output_file: Path) -> Path | None:
    """
    Reformat data from merged CSV file.
    Returns the path to the reformatted file (either existing or newly created).

    Args:
        input_path: Path to the input merged CSV file
        output_file: Path where to save the reformatted file

    Returns:
        Path to the reformatted file or None if failed
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
