from typing import Dict, Union, Set
from .http_handler import HTTPHandler
from .properties_manager import PropertiesManager
from .metrics_uploader import MetricsUploader


class NotionClient:
    """
    Main Notion API client that orchestrates HTTP handling,
    properties management, and metrics uploading.
    """

    def __init__(
        self,
        endpoint: str,
        headers: dict,
        database_id: str,
        max_concurrent_requests: int = 10,
    ):
        self.endpoint = endpoint
        self.headers = headers
        self.database_id = database_id

        # Initialize components
        self.http_handler = HTTPHandler(max_concurrent_requests=max_concurrent_requests)
        self.properties_manager = PropertiesManager(
            self.http_handler, endpoint, headers, database_id
        )
        self.metrics_uploader = MetricsUploader(
            self.http_handler, endpoint, headers, database_id
        )

        # Page cache for performance
        self._page_cache = {}

    async def close(self):
        """Close the HTTP client."""
        await self.http_handler.close()

    # Properties management methods
    async def get_properties(self) -> Dict | None:
        """Get all properties from the database."""
        return await self.properties_manager.get_properties()

    async def is_property_exists(self, property_name: str) -> bool:
        """Check if a property exists."""
        return await self.properties_manager.is_property_exists(property_name)

    async def create_property(
        self, property_name: str, property_type: str = "number", formula: dict = None
    ) -> bool:
        """Create a new property."""
        return await self.properties_manager.create_property(
            property_name, property_type, formula
        )

    async def delete_property(self, property_name: str) -> bool:
        """Delete a property."""
        return await self.properties_manager.delete_property(property_name)

    async def ensure_property_exists(
        self, property_name: str, property_type: str = "number"
    ) -> bool:
        """Ensure a property exists."""
        return await self.properties_manager.ensure_property_exists(
            property_name, property_type
        )

    async def get_number_properties(self) -> list:
        """Get all number type properties."""
        return await self.properties_manager.get_number_properties()

    async def cleanup_unused_properties(self, valid_metrics: Set[str]) -> bool:
        """Remove unused properties."""
        return await self.properties_manager.cleanup_unused_properties(valid_metrics)

    async def ensure_properties_exist_batch(
        self, property_names: list[str], property_type: str = "number"
    ) -> tuple[bool, list[str]]:
        """Ensure multiple properties exist in batch."""
        return await self.properties_manager.ensure_properties_exist_batch(
            property_names, property_type
        )

    # Metrics uploading methods
    async def get_page_id(self, symbol: str) -> str | None:
        """Get page ID for a symbol."""
        return await self.metrics_uploader.get_page_id(symbol, self._page_cache)

    async def upload_metric(
        self, symbol: str, metric: str, value: Union[float, str]
    ) -> bool:
        """Upload a single metric."""
        return await self.metrics_uploader.upload_metric(
            symbol, metric, value, self._page_cache
        )

    async def upload_metrics_batch(
        self, symbol: str, metrics_dict: Dict[str, Union[float, str]]
    ) -> bool:
        """Upload multiple metrics in a batch."""
        return await self.metrics_uploader.upload_metrics_batch(
            symbol, metrics_dict, self._page_cache
        )

    async def is_symbol_exists(self, symbol: str) -> bool:
        """Check if a symbol exists."""
        return await self.metrics_uploader.is_symbol_exists(symbol, self._page_cache)

    # Legacy compatibility methods for retry functionality
    async def _retry_request(
        self, request_func, max_retries: int = 3, base_delay: float = 1.0
    ):
        """
        Legacy method for backward compatibility.
        Delegates to http_handler.retry_request.
        """
        return await self.http_handler.retry_request(
            request_func, max_retries, base_delay
        )
