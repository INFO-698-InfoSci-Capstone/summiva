"""
API Documentation Module
======================
Provides consistent OpenAPI documentation configuration across services.
"""

from backend.core.imports import setup_imports
setup_imports()

from backend.core.docs.openapi import setup_openapi, get_openapi_schema

__all__ = ['setup_openapi', 'get_openapi_schema']