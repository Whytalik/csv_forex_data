import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import asyncio
from services.notion_client import NotionClient
from config.notion_settings import (
    NOTION_ENDPOINT,
    PROFILES,
    get_headers,
    get_database_id,
)
from config.metrics import NOTION_METRICS


async def clear_database_metrics(profile: str):
    try:
        print(f"\nClearing metrics for {profile}'s database...")
        client = NotionClient(
            NOTION_ENDPOINT,
            get_headers(profile),
            get_database_id(profile)
        )

        # Отримуємо всі сторінки з бази даних
        response = await client.client.post(
            f"{client.endpoint}/databases/{client.database_id}/query",
            headers=client.headers,
            json={}
        )
        response.raise_for_status()
        pages = response.json().get("results", [])

        if not pages:
            print(f"No pages found in {profile}'s database")
            return

        print(f"Found {len(pages)} pages")
        
        # Для кожної сторінки очищуємо всі числові властивості
        for page in pages:
            page_id = page["id"]
            title = page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text", "Unknown")
            
            # Створюємо словник з порожніми значеннями для всіх метрик
            properties = {}
            for group in NOTION_METRICS:
                for metric in NOTION_METRICS[group]:
                    if metric != "Date Range":  # Пропускаємо Date Range, бо це не числове значення
                        properties[metric] = {"number": None}

            # Оновлюємо сторінку
            update_response = await client.client.patch(
                f"{client.endpoint}/pages/{page_id}",
                headers=client.headers,
                json={"properties": properties}
            )
            update_response.raise_for_status()
            print(f"✅ Cleared metrics for {title}")

        await client.close()
        print(f"✅ Successfully cleared all metrics in {profile}'s database")

    except Exception as e:
        print(f"❌ Error clearing metrics for {profile}: {e}")


async def main():
    """Clear metrics in all databases"""
    for profile in PROFILES:
        await clear_database_metrics(profile)


if __name__ == "__main__":
    asyncio.run(main())
