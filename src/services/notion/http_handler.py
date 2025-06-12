import httpx
import asyncio
import random
from typing import Callable, Any


class HTTPHandler:
    """Handle HTTP requests with retry logic and rate limiting."""

    def __init__(self, timeout: float = 30.0, max_concurrent_requests: int = 10):
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def retry_request(
        self, request_func: Callable, max_retries: int = 3, base_delay: float = 1.0
    ) -> Any:
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

    async def post(self, url: str, headers: dict, json_data: dict) -> httpx.Response:
        """Make a POST request with semaphore protection."""
        async with self._semaphore:
            response = await self.client.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            return response

    async def patch(self, url: str, headers: dict, json_data: dict) -> httpx.Response:
        """Make a PATCH request with semaphore protection."""
        async with self._semaphore:
            response = await self.client.patch(url, headers=headers, json=json_data)
            response.raise_for_status()
            return response

    async def get(self, url: str, headers: dict) -> httpx.Response:
        """Make a GET request with semaphore protection."""
        async with self._semaphore:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response
