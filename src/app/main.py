from pathlib import Path
import asyncio
from services.csv_service import (
    collect_csv_files,
    merge_csv_files,
    reformat_data,
    create_timeframes_csv,
)
from config.settings import DATA_PATH
from config.metrics import NOTION_METRICS
from config.timeframes_config import TIMEFRAMES
from services.notion_client import NotionClient
from config.notion_settings import (
    NOTION_ENDPOINT,
    PROFILES,
    get_headers,
    get_database_id,
)
from services.metrics_service import MetricsService


async def process_data_and_calculate_metrics():
    """Process raw data, create timeframes and calculate metrics"""
    raw_data_root = Path(DATA_PATH["raw_data_path"])
    processed_data_root = Path(DATA_PATH["processed_data_path"])
    formatted_data_root = Path(DATA_PATH["formated_data_path"])
    timeframes_data_root = Path(DATA_PATH["timeframes_data_path"])

    # Create necessary directories
    formatted_data_root.mkdir(parents=True, exist_ok=True)
    processed_data_root.mkdir(parents=True, exist_ok=True)
    timeframes_data_root.mkdir(parents=True, exist_ok=True)

    metrics_by_symbol = {}

    for subdir in raw_data_root.iterdir():
        if subdir.is_dir():
            symbol = subdir.name
            print(f"Processing {symbol}...")

            collected_files = collect_csv_files(subdir)
            merged_file = merge_csv_files(collected_files, processed_data_root, symbol)

            if merged_file is not None:
                formatted_file = formatted_data_root / f"{symbol}_formatted.csv"
                formatted_path = reformat_data(merged_file, formatted_file)

                if formatted_path:
                    print(f"Successfully processed {symbol} data")
                    timeframes_files = create_timeframes_csv(
                        formatted_path, timeframes_data_root, symbol
                    )

                    metrics_service = MetricsService(timeframes_data_root)
                    metrics = metrics_service.calculate_all_metrics(symbol)

                    metrics_by_symbol[symbol] = metrics
                    print(f"✅ Calculated metrics for {symbol}")

    return metrics_by_symbol


async def upload_metrics_to_notion(metrics: dict):
    """Upload calculated metrics to Notion for each profile"""
    for profile in PROFILES:
        try:
            headers = get_headers(profile)
            database_id = get_database_id(profile)

            notion_client = NotionClient(NOTION_ENDPOINT, headers, database_id)

            for group in NOTION_METRICS:
                for metric in NOTION_METRICS[group]:
                    await notion_client.ensure_property_exists(metric, "number")

            for symbol, symbol_metrics in metrics.items():
                print(f"Uploading metrics for {symbol} to {profile}'s Notion database")
                # TODO: Add actual upload logic here

            await notion_client.close()
            print(f"✅ Successfully processed metrics for {profile}")

        except Exception as e:
            print(f"❌ Error processing profile {profile}: {e}")
            continue


async def main():
    """Main execution function"""
    metrics = await process_data_and_calculate_metrics()
    await upload_metrics_to_notion(metrics)


if __name__ == "__main__":
    asyncio.run(main())
