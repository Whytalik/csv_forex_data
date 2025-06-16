from pathlib import Path
import pandas as pd  # type: ignore


def merge_csv_files(
    csv_files: list[Path], output_dir: Path, prefix: str
) -> Path | None:
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
        print(f"ℹ️ Merged file already exists: {output_file.name}")
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
        print(f"✅ Merged data saved to {output_file.name}")
        return output_file
    except Exception as e:
        print(f"❌ Error saving merged file: {e}")
        return None
