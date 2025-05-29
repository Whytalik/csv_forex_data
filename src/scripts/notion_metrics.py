import json
import httpx
from config.notion_settings import NOTION_ENDPOINT, HEADERS, PAIRS_DATABASE_ID


def get_database_properties():
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{NOTION_ENDPOINT}/databases/{PAIRS_DATABASE_ID}", headers=HEADERS
            )
            response.raise_for_status()
            database = response.json()
            return database.get("properties", {})
    except httpx.HTTPError as e:
        print(f"Error: {e}")
        return None


def format_metrics_config(properties):
    return list(properties.keys())


def save_metrics_config(metrics):
    config_content = (
        f"NOTION_METRICS = {json.dumps(metrics, indent=4, ensure_ascii=False)}"
    )

    try:
        with open("/config/metrics.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("Metrics config saved in config/metrics.py")
        return True
    except Exception as e:
        print(f"Error saving metrics config: {e}")
        return False


def main():
    properties = get_database_properties()
    if properties:
        metrics = format_metrics_config(properties)
        save_metrics_config(metrics)


if __name__ == "__main__":
    main()
