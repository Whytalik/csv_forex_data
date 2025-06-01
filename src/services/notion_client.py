import httpx


class NotionClient:
    def __init__(self, endpoint, headers, database_id):
        self.endpoint = endpoint
        self.headers = headers
        self.database_id = database_id
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))

    async def close(self):
        await self.client.aclose()

    async def get_properties(self) -> dict | None:
        try:
            response = await self.client.get(
                f"{self.endpoint}/databases/{self.database_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            database = response.json()
            return database.get("properties", {})
        except httpx.HTTPError as e:
            print(f"❌ Error fetching properties: {e}")
            return None

    async def is_property_exists(self, property_name: str) -> bool:
        properties = await self.get_properties()
        return properties is not None and property_name in properties

    async def create_property(
        self, property_name: str, property_type: str = "number", formula: dict = None
    ) -> bool:
        if await self.is_property_exists(property_name):
            print(f"ℹ️ Property '{property_name}' already exists. Skipping creation.")
            return True

        try:
            properties = {property_name: {property_type: {}}}
            if property_type == "formula" and formula:
                properties[property_name] = {"formula": formula}

            response = await self.client.patch(
                f"{self.endpoint}/databases/{self.database_id}",
                headers=self.headers,
                json={"properties": properties},
            )
            response.raise_for_status()
            print(f"✅ Created property: {property_name}")
            return True
        except httpx.HTTPError as e:
            print(f"❌ Error creating property: {e}")
            return False

    async def ensure_property_exists(
        self, property_name: str, property_type: str = "number"
    ) -> bool:
        if await self.is_property_exists(property_name):
            print(f"ℹ️ Property '{property_name}' already exists.")
            return True
        return await self.create_property(property_name, property_type)

    async def upload_metric(self, symbol: str, metric: str, value: float | str) -> bool:
        try:
            # Спочатку знаходимо сторінку для даної валютної пари
            response = await self.client.post(
                f"{self.endpoint}/databases/{self.database_id}/query",
                headers=self.headers,
                json={
                    "filter": {"property": "title", "title": {"equals": symbol.upper()}}
                },
            )
            response.raise_for_status()
            pages = response.json().get("results", [])

            if not pages:
                print(f"❌ No page found for symbol {symbol}")
                return False

            page_id = pages[0]["id"]
            if metric == "Date Range":
                property_value = {
                    "rich_text": [
                        {
                            "text": {"content": str(value)},
                            "annotations": {"bold": True, "color": "pink"},
                        }
                    ]
                }
            else:
                property_value = {"number": float(value)}

            # Оновлюємо властивість метрики для знайденої сторінки
            data = {"properties": {metric: property_value}}

            response = await self.client.patch(
                f"{self.endpoint}/pages/{page_id}", headers=self.headers, json=data
            )
            response.raise_for_status()
            print(f"✅ Updated metric '{metric}' for {symbol}")
            return True

        except httpx.HTTPError as e:
            print(f"❌ Error uploading metric '{metric}' for {symbol}: {e}")
            return False

    async def is_symbol_exists(self, symbol: str) -> bool:
        try:
            response = await self.client.post(
                f"{self.endpoint}/databases/{self.database_id}/query",
                headers=self.headers,
                json={
                    "filter": {"property": "title", "title": {"equals": symbol.upper()}}
                },
            )
            response.raise_for_status()
            pages = response.json().get("results", [])
            return len(pages) > 0
        except httpx.HTTPError as e:
            print(f"❌ Error checking if symbol exists: {e}")
            return False
