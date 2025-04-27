# src/backend/core/service_registry.py
from typing import Dict, Optional
import httpx
import logging
from config.settings.settings import settings

logger = logging.getLogger(__name__)

class ServiceRegistry:
    _instance = None
    _services: Dict[str, str]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._services = {
                "auth": settings.AUTH_SERVICE_URL,
                "document": settings.DOCUMENT_SERVICE_URL,
                "search": settings.SEARCH_SERVICE_URL,
                "tagging": settings.TAGGING_SERVICE_URL,
                "grouping": settings.GROUPING_SERVICE_URL,
            }
        return cls._instance

    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the URL for a service by name."""
        return self._services.get(service_name)

    def register_service(self, service_name: str, url: str) -> None:
        """Register or update a service."""
        self._services[service_name] = url
        logger.info(f"Registered service: {service_name} at {url}")

    def deregister_service(self, service_name: str) -> None:
        """Deregister a service."""
        if self._services.pop(service_name, None):
            logger.info(f"Deregistered service: {service_name}")

    async def health_check(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        url = self.get_service_url(service_name)
        if not url:
            logger.warning(f"Service {service_name} not found for health check.")
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                return response.status_code == 200
        except httpx.HTTPError as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

    async def discover_services(self) -> Dict[str, str]:
        """Discover and return healthy services."""
        available_services = {}
        for service_name, url in self._services.items():
            if await self.health_check(service_name):
                available_services[service_name] = url
        return available_services