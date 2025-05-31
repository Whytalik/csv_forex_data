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


async def get_formula_metrics():
    try:
        # Отримуємо формули з бази даних Whytalik
        whytalik_client = NotionClient(
            NOTION_ENDPOINT, get_headers(PROFILES[1]), get_database_id(PROFILES[1])
        )

        # Отримуємо всі формули
        properties = await whytalik_client.get_properties()
        formula_metrics = {}

        if properties:
            print("\nFormula metrics from Whytalik's database:")
            print("-" * 50)

            for prop_name, prop_details in properties.items():
                if prop_details.get("type") == "formula":
                    formula_metrics[prop_name] = prop_details.get("formula", {})
                    print(f"- {prop_name}")
                    print(
                        f"  Formula: {prop_details.get('formula', {}).get('expression', 'N/A')}"
                    )

        # Якщо знайшли формули, додаємо їх до бази даних vital
        if formula_metrics:
            print("\nAdding formulas to vital's database...")
            vital_client = NotionClient(
                NOTION_ENDPOINT, get_headers(PROFILES[0]), get_database_id(PROFILES[0])
            )

            # Додаємо кожну формулу
            for metric_name, formula in formula_metrics.items():
                success = await vital_client.create_property(
                    metric_name, "formula", formula
                )
                if success:
                    print(f"✅ Added formula: {metric_name}")
                else:
                    print(f"❌ Failed to add formula: {metric_name}")

            await vital_client.close()

        await whytalik_client.close()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(get_formula_metrics())
