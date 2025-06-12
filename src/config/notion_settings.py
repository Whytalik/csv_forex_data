API_SETTINGS = {
    "Whytalik": {
        "API_KEY": "secret_sl5BQuN2XSLk2uVZXj0JN3kF8jp5kgbLWFpRGXNmpSb",
        "DATABASE_ID": "20c2e1b676d4810684a2cd74e78d4770",
    },
    "Mordan": {
        "API_KEY": "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",
        "DATABASE_ID": "17a56d60af3681e98b8dd68cf3d7fa5b",
    },
    "Infobase": {
        "API_KEY": "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",
        "DATABASE_ID": "20d56d60af3680a09982e49ba70107cf",
    },
}

PROFILES = list(API_SETTINGS.keys())

NOTION_ENDPOINT = "https://api.notion.com/v1"


def get_headers(profile: str) -> dict:
    if profile not in API_SETTINGS:
        raise ValueError(f"Unknown profile: {profile}")
    return {
        "Authorization": f"Bearer {API_SETTINGS[profile]['API_KEY']}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def get_database_id(profile: str) -> str:
    if profile not in API_SETTINGS:
        raise ValueError(f"Unknown profile: {profile}")
    return API_SETTINGS[profile]["DATABASE_ID"]
