from pathlib import Path
import asyncio
from services.csv_service import collect_csv_files, merge_csv_files, reformat_data
from config.settings import DATA_PATH
from config.metrics import NOTION_METRICS
from services.notion_client import NotionClient
from config.notion_settings import (
    NOTION_ENDPOINT,
    PROFILES,
    get_headers,
    get_database_id,
)


async def run_for_profile(profile: str):
    headers = get_headers(profile)
    database_id = get_database_id(profile)

    notion_client = NotionClient(NOTION_ENDPOINT, headers, database_id)

    for group in NOTION_METRICS:
        for metric in NOTION_METRICS[group]:
            await notion_client.ensure_property_exists(metric, "number")

    await notion_client.close()


async def main():
    await asyncio.gather(*(run_for_profile(profile) for profile in PROFILES))


if __name__ == "__main__":
    asyncio.run(main())

    """raw_data_root = Path(DATA_PATH["raw_data_path"])
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
                reformat_data(merged_df, formatted_output)"""
