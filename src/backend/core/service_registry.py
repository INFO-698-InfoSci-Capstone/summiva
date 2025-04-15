from typing import Dict, Optional
import httpx
from fastapi import HTTPException
import logging
from core.config.settings import settings

logger = logging.getLogger(__name__)

class ServiceRegistry:
    _instance = None
    _services: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._services:
            self._services = {
                "auth": settings.AUTH_SERVICE_URL,
                "document": settings.DOCUMENT_SERVICE_URL,
                "search": settings.SEARCH_SERVICE_URL,
                "tagging": settings.TAGGING_SERVICE_URL,
                "grouping": settings.GROUPING_SERVICE_URL
            }

    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the URL for a service by name"""
        return self._services.get(service_name)

    def register_service(self, service_name: str, url: str) -> None:
        """Register a new service or update an existing one"""
        self._services[service_name] = url
        logger.info(f"Service {service_name} registered at {url}")

    def deregister_service(self, service_name: str) -> None:
        """Remove a service from the registry"""
        if service_name in self._services:
            del self._services[service_name]
            logger.info(f"Service {service_name} deregistered")

    async def health_check(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        url = self.get_service_url(service_name)
        if not url:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

    async def discover_services(self) -> Dict[str, str]:
        """Discover all available services"""
        available_services = {}
        for service_name, url in self._services.items():
            if await self.health_check(service_name):
                available_services[service_name] = url
        return available_services 