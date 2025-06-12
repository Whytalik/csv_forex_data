from typing import Dict, Union
from .http_handler import HTTPHandler


class MetricsUploader:
    """Handle uploading metrics to Notion database pages."""

    def __init__(
        self, http_handler: HTTPHandler, endpoint: str, headers: dict, database_id: str
    ):
        self.http_handler = http_handler
        self.endpoint = endpoint
        self.headers = headers
        self.database_id = database_id

    async def get_page_id(self, symbol: str, page_cache: dict) -> str | None:
        """Get page ID for a symbol, using cache if available."""
        if symbol.upper() in page_cache:
            return page_cache[symbol.upper()]

        try:
            response = await self.http_handler.post(
                f"{self.endpoint}/databases/{self.database_id}/query",
                self.headers,
                {
                    "filter": {
                        "property": "title",
                        "title": {"equals": symbol.upper()},
                    }
                },
            )
            pages = response.json().get("results", [])

            if pages:
                page_id = pages[0]["id"]
                page_cache[symbol.upper()] = page_id
                return page_id

            return None
        except Exception as e:
            print(f"❌ Error fetching page_id for {symbol}: {e}")
            return None

    async def upload_metric(
        self, symbol: str, metric: str, value: Union[float, str], page_cache: dict
    ) -> bool:
        """Upload a single metric to a symbol's page."""
        try:
            response = await self.http_handler.post(
                f"{self.endpoint}/databases/{self.database_id}/query",
                self.headers,
                {"filter": {"property": "title", "title": {"equals": symbol.upper()}}},
            )
            pages = response.json().get("results", [])

            if not pages:
                print(f"❌ No page found for symbol {symbol}")
                return False

            page_id = pages[0]["id"]
            property_value = {"number": float(value)}

            data = {"properties": {metric: property_value}}

            response = await self.http_handler.patch(
                f"{self.endpoint}/pages/{page_id}", self.headers, data
            )
            print(f"✅ Updated metric '{metric}' for {symbol}")
            return True
        except Exception as e:
            print(f"❌ Error uploading metric '{metric}' for {symbol}: {e}")
            return False

    async def upload_metrics_batch(
        self, symbol: str, metrics_dict: Dict[str, Union[float, str]], page_cache: dict
    ) -> bool:
        """Upload multiple metrics to a symbol's page in a single request."""
        try:
            page_id = await self.get_page_id(symbol, page_cache)
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

            response = await self.http_handler.patch(
                f"{self.endpoint}/pages/{page_id}", self.headers, data
            )

            print(f"✅ Updated {len(properties)} metrics for {symbol}")
            return True

        except Exception as e:
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

    async def is_symbol_exists(self, symbol: str, page_cache: dict) -> bool:
        """Check if a symbol exists in the database."""
        page_id = await self.get_page_id(symbol, page_cache)
        return page_id is not None
