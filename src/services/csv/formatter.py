from pathlib import Path
import pandas as pd  # type: ignore
from datetime import datetime, timedelta


def reformat_data(input_path: Path, output_file: Path) -> Path | None:
    if output_file.exists():
        print(f"ℹ️ Reformatted file already exists: {output_file.name}")
        return output_file

    try:
        df = pd.read_csv(
            input_path,
            sep=";",
            header=None,
            names=["datetime", "open", "high", "low", "close"],
        )
        df["datetime"] = df["datetime"].apply(adjust_datetime)

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


def adjust_datetime(dt_str):
    dt = datetime.strptime(str(dt_str), "%Y%m%d %H%M%S")
    return dt.strftime("%Y-%m-%d %H:%M:%S")
