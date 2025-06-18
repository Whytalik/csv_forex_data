import sys
from pathlib import Path
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from services.csv import (
    collect_csv_files,
    merge_csv_files,
    reformat_data,
    create_timeframes_csv,
)
from config.settings import DATA_PATH
from utils.profile_metrics import (
    get_metrics_for_profile,
    group_metrics_by_category,
    filter_profile_metrics_by_category,
)
from services.notion import NotionClient
from config.notion_settings import (
    NOTION_ENDPOINT,
    PROFILES,
    get_headers,
    get_database_id,
)
from services.metrics_service import MetricsService


async def process_single_symbol(
    symbol_dir: Path,
    processed_data_root: Path,
    formatted_data_root: Path,
    timeframes_data_root: Path,
    executor: ThreadPoolExecutor,
) -> tuple[str, dict] | None:
    """Process a single symbol using thread executor for CPU-intensive tasks"""
    try:
        symbol = symbol_dir.name
        print(f"🔄 Processing {symbol}...")

        loop = asyncio.get_event_loop()

        collected_files = await loop.run_in_executor(
            executor, collect_csv_files, symbol_dir
        )

        merged_file = await loop.run_in_executor(
            executor, merge_csv_files, collected_files, processed_data_root, symbol
        )

        if merged_file is None:
            return None

        year = merged_file.stem.split("_")[-1]
        formatted_file = formatted_data_root / f"{symbol}_formatted_{year}.csv"

        formatted_path = await loop.run_in_executor(
            executor, reformat_data, merged_file, formatted_file
        )

        if formatted_path is None:
            return None

        await loop.run_in_executor(
            executor,
            create_timeframes_csv,
            formatted_path,
            timeframes_data_root,
            symbol,
        )

        print(f"✅ Successfully processed {symbol} data")

        metrics_service = MetricsService(timeframes_data_root)
        flat_metrics = await loop.run_in_executor(
            executor, metrics_service.calculate_all_metrics, symbol
        )

        grouped_metrics = group_metrics_by_category(flat_metrics)
        print(f"✅ Calculated metrics for {symbol}")
        return symbol, grouped_metrics

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")
        return None


async def process_data_and_calculate_metrics():
    """Process all symbols in parallel with limited concurrency"""
    start_time = time.time()

    src_path = Path(__file__).parent.parent

    raw_data_root = src_path / DATA_PATH["raw_data_path"]
    processed_data_root = src_path / DATA_PATH["processed_data_path"]
    formatted_data_root = src_path / DATA_PATH["formated_data_path"]
    timeframes_data_root = src_path / DATA_PATH["timeframes_data_path"]

    # Create directories
    for directory in [formatted_data_root, processed_data_root, timeframes_data_root]:
        directory.mkdir(parents=True, exist_ok=True)

    # Get all symbol directories
    symbol_dirs = [subdir for subdir in raw_data_root.iterdir() if subdir.is_dir()]

    if not symbol_dirs:
        print("⚠️ No symbol directories found")
        return {}

    print(f"🚀 Starting parallel processing of {len(symbol_dirs)} symbols...")

    # Create thread executor for CPU-intensive tasks
    max_workers = min(5, len(symbol_dirs))  # Adjust based on your system

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_workers)

        async def process_with_semaphore(symbol_dir):
            async with semaphore:
                return await process_single_symbol(
                    symbol_dir,
                    processed_data_root,
                    formatted_data_root,
                    timeframes_data_root,
                    executor,
                )

        # Process all symbols in parallel
        tasks = [process_with_semaphore(symbol_dir) for symbol_dir in symbol_dirs]
        print(
            f"📊 Processing {len(tasks)} symbols in parallel (max {max_workers} concurrent)..."
        )
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect successful results
    metrics_by_symbol = {}
    successful = 0
    failed = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed += 1
            symbol_name = symbol_dirs[i].name if i < len(symbol_dirs) else "unknown"
            print(f"❌ Processing failed for {symbol_name}: {result}")
        elif result is not None:
            symbol, metrics = result
            metrics_by_symbol[symbol] = metrics
            successful += 1
        else:
            failed += 1

    elapsed_time = time.time() - start_time
    print(
        f"✅ Completed processing in {elapsed_time:.2f}s: {successful} successful, {failed} failed"
    )

    return metrics_by_symbol


async def upload_metrics_to_notion(metrics: dict):
    """Upload calculated metrics to Notion for each profile with parallel processing"""

    async def process_profile(profile: str):
        """Process metrics for a single profile"""
        try:
            print(f"\n📤 Processing metrics for {profile}'s database...")
            headers = get_headers(profile)
            database_id = get_database_id(profile)
            notion_client = NotionClient(
                NOTION_ENDPOINT, headers, database_id, max_concurrent_requests=15
            )

            print("🔧 Ensuring all properties exist...")
            profile_metrics = get_metrics_for_profile(profile)

            # Collect all metrics names into a single list
            all_metrics_names = []
            for category, metrics_list in profile_metrics.items():
                all_metrics_names.extend(metrics_list)

            # Ensure all properties exist in batch
            success, created_properties = (
                await notion_client.ensure_properties_exist_batch(
                    all_metrics_names, "number"
                )
            )

            # If any properties were newly created, add a small delay to allow Notion API to register them
            if created_properties:
                print(
                    f"⏳ Waiting for Notion API to register {len(created_properties)} newly created properties..."
                )
                await asyncio.sleep(3)

            print("📊 Preparing metrics for batch upload...")
            upload_tasks = []

            for symbol, symbol_metrics in metrics.items():
                if not await notion_client.is_symbol_exists(symbol.upper()):
                    print(f"⚠️ Skipping {symbol} - not found in {profile}'s database")
                    continue

                # Filter metrics for specific profile
                filtered_symbol_metrics = filter_profile_metrics_by_category(
                    symbol_metrics, profile
                )

                symbol_metrics_to_upload = {}
                for category, metrics_list in profile_metrics.items():
                    if category in filtered_symbol_metrics and isinstance(
                        filtered_symbol_metrics[category], dict
                    ):
                        for metric_name, value in filtered_symbol_metrics[
                            category
                        ].items():
                            if metric_name in metrics_list:
                                if isinstance(value, (int, float)):
                                    symbol_metrics_to_upload[metric_name] = round(
                                        value, 2
                                    )
                                else:
                                    symbol_metrics_to_upload[metric_name] = value

                if symbol_metrics_to_upload:
                    upload_tasks.append(
                        notion_client.upload_metrics_batch(
                            symbol, symbol_metrics_to_upload
                        )
                    )

            if upload_tasks:
                print(
                    f"🚀 Uploading metrics for {len(upload_tasks)} symbols in parallel..."
                )
                results = await asyncio.gather(*upload_tasks, return_exceptions=True)

                successful = sum(1 for result in results if result is True)
                failed = len(results) - successful
                print(
                    f"✅ Successfully uploaded metrics for {successful}/{len(upload_tasks)} symbols"
                )
                if failed > 0:
                    print(f"❌ Failed to upload metrics for {failed} symbols")

            await notion_client.close()
            print(f"✅ Successfully processed metrics for {profile}")
            return True

        except Exception as e:
            print(f"❌ Error processing profile {profile}: {e}")
            return False

    print("🚀 Starting parallel processing of all profiles...")
    profile_tasks = [process_profile(profile) for profile in PROFILES]
    results = await asyncio.gather(*profile_tasks, return_exceptions=True)

    # Summary
    successful_profiles = sum(1 for result in results if result is True)
    failed_profiles = len(PROFILES) - successful_profiles
    print(
        f"\n🎉 Processing complete! {successful_profiles}/{len(PROFILES)} profiles processed successfully"
    )
    if failed_profiles > 0:
        print(f"❌ {failed_profiles} profiles failed")

    return successful_profiles == len(PROFILES)


async def main():
    """Main function with optimized error handling and performance monitoring"""
    try:
        print("🚀 Starting Forex Data Processing Pipeline...")
        start_time = time.time()

        # Step 1: Process data and calculate metrics
        print("\n📊 Step 1: Processing data and calculating metrics...")
        metrics = await process_data_and_calculate_metrics()

        if not metrics:
            print("❌ No metrics calculated. Exiting.")
            return

        step1_time = time.time() - start_time
        print(f"✅ Step 1 completed in {step1_time:.2f}s")

        # Step 2: Upload metrics to Notion
        print("\n📤 Step 2: Uploading metrics to Notion...")
        upload_start = time.time()

        upload_success = await upload_metrics_to_notion(metrics)

        upload_time = time.time() - upload_start
        total_time = time.time() - start_time

        print(f"\n🎯 Performance Summary:")
        print(f"   • Data processing: {step1_time:.2f}s")
        print(f"   • Notion upload: {upload_time:.2f}s")
        print(f"   • Total time: {total_time:.2f}s")
        print(f"   • Symbols processed: {len(metrics)}")
        print(f"   • Upload success: {'✅' if upload_success else '❌'}")

        if upload_success:
            print("\n🎉 All processing completed successfully!")
        else:
            print("\n⚠️ Processing completed with some upload failures")

    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error in main process: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
