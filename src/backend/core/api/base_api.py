"""
Base API Router Configuration
============================
Provides a standardized way to create and configure FastAPI routers.
"""

from fastapi import APIRouter, Depends, Security
from typing import List, Dict, Any, Optional, Callable, Type

from backend.core.imports import setup_imports
setup_imports()

from config.logs.logging import setup_logging

# Get logger for this module
logger = setup_logging("core.api")

def create_api_router(
    tags: List[str],
    prefix: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    responses: Optional[Dict[int, Dict[str, Any]]] = None,
    deprecated: bool = False,
    include_in_schema: bool = True,
) -> APIRouter:
    """
    Create a standardized API router with common configuration.
    
    Args:
        tags: A list of tags for organizing routes in the OpenAPI docs
        prefix: Optional URL prefix for all routes in this router
        dependencies: Optional list of dependencies to apply to all routes
        responses: Optional common responses documentation
        deprecated: Whether all routes in this router are marked as deprecated
        include_in_schema: Whether to include routes in the OpenAPI schema
        
    Returns:
        Configured APIRouter
    """
    # Standard responses for all APIs
    standard_responses = {
        400: {"description": "Bad Request - Invalid input parameters"},
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Resource does not exist"},
        500: {"description": "Internal Server Error"},
    }
    
    # Merge with custom responses if provided
    if responses:
        standard_responses.update(responses)
    
    # Create router with standard configuration
    router = APIRouter(
        tags=tags,
        prefix=prefix,
        dependencies=dependencies or [],
        responses=standard_responses,
        deprecated=deprecated,
        include_in_schema=include_in_schema,
    )
    
    logger.debug(f"Created API router with tags {tags} and prefix {prefix}")
    return router