"""
API Client Module
==============
Provides standardized clients for service-to-service communication.
"""

from backend.core.imports import setup_imports
setup_imports()

from backend.core.api_client.base import BaseAPIClient
from backend.core.api_client.factory import get_service_client

__all__ = ['BaseAPIClient', 'get_service_client']