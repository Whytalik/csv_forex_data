from config.notion_settings import NOTION_ENDPOINT, HEADERS, PAIRS_DATABASE_ID
from config.metrics import NOTION_METRICS
from services.notion_client import NotionClient

if __name__ == "__main__":
    client = NotionClient(NOTION_ENDPOINT, HEADERS, PAIRS_DATABASE_ID)

    for group_name, metrics in NOTION_METRICS.items():
        for property_name in metrics:
            print(f"Processing {property_name} in group {group_name}")
            client.ensure_property_exists(property_name, "number")
