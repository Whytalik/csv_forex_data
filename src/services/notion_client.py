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
        self, property_name: str, property_type: str = "number"
    ) -> bool:
        if await self.is_property_exists(property_name):
            print(f"ℹ️ Property '{property_name}' already exists. Skipping creation.")
            return True

        try:
            response = await self.client.patch(
                f"{self.endpoint}/databases/{self.database_id}",
                headers=self.headers,
                json={"properties": {property_name: {property_type: {}}}},
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
