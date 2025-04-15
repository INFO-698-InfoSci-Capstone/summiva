from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class BaseAPIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """Make an HTTP request with retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable"
            )

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("POST", endpoint, json=json)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("PUT", endpoint, json=json)

    async def delete(self, endpoint: str) -> Any:
        return await self._request("DELETE", endpoint)

    async def close(self):
        await self.client.aclose() 