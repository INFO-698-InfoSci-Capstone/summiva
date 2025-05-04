"""
Core Schemas Module
=================
Provides standardized Pydantic models for consistent API responses across services.
"""

from backend.core.imports import setup_imports
setup_imports()

from backend.core.schemas.base import (
    BaseModel,
    BaseConfig,
    APIResponse,
    PaginatedResponse,
    ErrorResponse
)

from backend.core.schemas.pagination import (
    PageParams,
    SortParams,
    Pagination
)

__all__ = [
    # Base models
    'BaseModel',
    'BaseConfig',
    'APIResponse',
    'ErrorResponse',
    'PaginatedResponse',
    # Pagination
    'PageParams',
    'SortParams',
    'Pagination'
]