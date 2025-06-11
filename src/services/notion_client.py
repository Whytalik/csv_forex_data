import httpx
import asyncio
import time
import random


class NotionClient:
    def __init__(self, endpoint, headers, database_id, max_concurrent_requests=10):
        self.endpoint = endpoint
        self.headers = headers
        self.database_id = database_id
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        self._page_cache = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def _retry_request(self, request_func, max_retries=3, base_delay=1.0):
        """
        Retry a request with exponential backoff for handling 503 and other transient errors
        """
        for attempt in range(max_retries + 1):
            try:
                result = await request_func()
                return result
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [
                    503,
                    502,
                    504,
                    429,
                ]:  # Service unavailable, bad gateway, gateway timeout, rate limit
                    if attempt == max_retries:
                        raise  # Re-raise on final attempt

                    # Calculate delay with exponential backoff and jitter
                    delay = base_delay * (2**attempt) + random.uniform(0, 1)
                    print(
                        f"⚠️ Notion API error {e.response.status_code}, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                else:
                    raise  # Re-raise non-retryable errors immediately
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == max_retries:
                    raise

                delay = base_delay * (2**attempt) + random.uniform(0, 1)
                print(
                    f"⚠️ Connection error, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                await asyncio.sleep(delay)

        return None  # Should never reach here

    async def close(self):
        await self.client.aclose()

    async def get_page_id(self, symbol: str) -> str | None:
        if symbol.upper() in self._page_cache:
            return self._page_cache[symbol.upper()]

        async with self._semaphore:
            try:
                response = await self.client.post(
                    f"{self.endpoint}/databases/{self.database_id}/query",
                    headers=self.headers,
                    json={
                        "filter": {
                            "property": "title",
                            "title": {"equals": symbol.upper()},
                        }
                    },
                )
                response.raise_for_status()
                pages = response.json().get("results", [])

                if pages:
                    page_id = pages[0]["id"]
                    self._page_cache[symbol.upper()] = page_id
                    return page_id

                return None
            except httpx.HTTPError as e:
                print(f"❌ Error fetching page_id for {symbol}: {e}")
                return None

        async def _make_request():
            async with self._semaphore:
                response = await self.client.get(
                    f"{self.endpoint}/databases/{self.database_id}",
                    headers=self.headers,
                )
                response.raise_for_status()
                database = response.json()
                return database.get("properties", {})

        try:
            return await self._retry_request(_make_request)
        except Exception as e:
            print(f"❌ Error fetching properties after retries: {e}")
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

        async with self._semaphore:
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
            property_value = {"number": float(value)}

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

    async def upload_metrics_batch(self, symbol: str, metrics_dict: dict) -> bool:
        try:
            page_id = await self.get_page_id(symbol)
            if not page_id:
                print(f"❌ No page found for symbol {symbol}")
                return False

            properties = {}
            invalid_metrics = []

            for metric_name, value in metrics_dict.items():
                try:
                    # Validate numeric value
                    if value is None or (
                        isinstance(value, str) and value.strip() == ""
                    ):
                        print(f"⚠️ Skipping empty metric {metric_name} for {symbol}")
                        continue

                    # Check for inf or nan values
                    float_value = float(value)
                    if (
                        not isinstance(float_value, (int, float))
                        or float_value != float_value
                        or float_value == float("inf")
                        or float_value == float("-inf")
                    ):
                        print(
                            f"⚠️ Skipping invalid metric {metric_name}={value} for {symbol}"
                        )
                        invalid_metrics.append(f"{metric_name}={value}")
                        continue

                    rounded_value = round(float_value, 2)
                    properties[metric_name] = {"number": rounded_value}

                except (ValueError, TypeError) as ve:
                    print(
                        f"⚠️ Invalid value for metric {metric_name}={value} for {symbol}: {ve}"
                    )
                    invalid_metrics.append(f"{metric_name}={value}")
                    continue

            if not properties:
                print(f"⚠️ No valid metrics to upload for {symbol}")
                return False

            if invalid_metrics:
                print(
                    f"⚠️ Skipped {len(invalid_metrics)} invalid metrics for {symbol}: {invalid_metrics[:5]}..."
                )

            data = {"properties": properties}

            async with self._semaphore:
                response = await self.client.patch(
                    f"{self.endpoint}/pages/{page_id}", headers=self.headers, json=data
                )
                response.raise_for_status()

            print(f"✅ Updated {len(properties)} metrics for {symbol}")
            return True

        except httpx.HTTPError as e:
            print(f"❌ Error uploading metrics batch for {symbol}: {e}")
            # Try to get more detailed error information
            try:
                error_detail = (
                    e.response.json()
                    if hasattr(e, "response") and e.response
                    else "No response details"
                )
                print(f"❌ Error details: {error_detail}")
            except:
                print(f"❌ Could not parse error details")

            return False

    async def is_symbol_exists(self, symbol: str) -> bool:
        page_id = await self.get_page_id(symbol)
        return page_id is not None
