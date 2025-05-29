from pathlib import Path
from services.csv_service import collect_csv_files, merge_csv_files, reformat_data
from config.settings import DATA_PATH

if __name__ == "__main__":
    raw_data_root = Path(DATA_PATH["raw_data_path"])
    processed_data_root = Path(DATA_PATH["processed_data_path"])
    formatted_data_root = Path(DATA_PATH["formated_data_path"])

    formatted_data_root.mkdir(parents=True, exist_ok=True)

    for subdir in raw_data_root.iterdir():
        if subdir.is_dir():
            collected_files = collect_csv_files(subdir)
            merged_output = processed_data_root / f"{subdir.name}_merged.csv"
            merged_df = merge_csv_files(collected_files, merged_output)

            if merged_df is not None:
                formatted_output = formatted_data_root / f"{subdir.name}_formatted.csv"
                reformat_data(merged_df, formatted_output)
