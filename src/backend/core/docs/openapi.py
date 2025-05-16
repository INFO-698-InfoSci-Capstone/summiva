"""
OpenAPI Documentation Configuration
================================
Provides utilities to standardize OpenAPI documentation across services.
"""
from typing import Dict, Any, List, Optional, Callable
import os
from config.logging.logging import setup_logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from backend.core.imports import setup_imports
setup_imports()

from config.settings import settings

# Get logger for this module
logger = setup_logging("core.docs")


def get_openapi_schema(
    app: FastAPI,
    service_name: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a customized OpenAPI schema for a service
    
    Args:
        app: FastAPI application
        service_name: Name of the service
        title: API title (defaults to '{service_name} API')
        description: API description
        version: API version
        
    Returns:
        Dict[str, Any]: OpenAPI schema
    """
    # Set defaults
    title = title or f"{service_name.title()} API"
    description = description or f"Summiva {service_name.title()} Service API"
    version = version or getattr(settings, "API_VERSION", "1.0.0")
    
    # Get company info from settings
    company_name = getattr(settings, "COMPANY_NAME", "Summiva")
    company_url = getattr(settings, "COMPANY_URL", "https://summiva.ai")
    contact_email = getattr(settings, "CONTACT_EMAIL", "support@summiva.ai")
    license_name = getattr(settings, "LICENSE_NAME", "Proprietary")
    
    # Get base schema
    if app.openapi_schema:
        return app.openapi_schema
    
    # Generate custom schema
    openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        routes=app.routes,
    )
    
    # Add server information
    server_url = getattr(settings, f"{service_name.upper()}_API_URL", None)
    if server_url:
        openapi_schema["servers"] = [{"url": server_url}]
    
    # Add service logo
    service_logo_url = getattr(settings, f"{service_name.upper()}_LOGO_URL", None)
    logo_url = service_logo_url or getattr(settings, "API_LOGO_URL", None)
    
    # Customize info section
    openapi_schema["info"]["contact"] = {
        "name": company_name,
        "url": company_url,
        "email": contact_email,
    }
    
    openapi_schema["info"]["license"] = {
        "name": license_name
    }
    
    if logo_url:
        openapi_schema["info"]["x-logo"] = {
            "url": logo_url,
            "altText": f"{company_name} logo"
        }
    
    # Add custom styling
    openapi_schema["x-tagGroups"] = [
        {
            "name": "API Endpoints",
            "tags": [tag["name"] for tag in openapi_schema.get("tags", [])]
        }
    ]
    
    # Security definitions
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Global security requirement
    openapi_schema["security"] = [
        {"bearerAuth": []}
    ]
    
    # Store it for reuse
    app.openapi_schema = openapi_schema
    return openapi_schema


def setup_openapi(
    app: FastAPI,
    service_name: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    docs_url: Optional[str] = "/docs",
    redoc_url: Optional[str] = "/redoc",
    openapi_url: Optional[str] = "/openapi.json",
    swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
    swagger_ui_parameters: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Set up OpenAPI documentation for a FastAPI application
    
    Args:
        app: FastAPI application
        service_name: Name of the service
        title: API title (defaults to '{service_name} API')
        description: API description
        version: API version
        docs_url: URL for the Swagger UI docs
        redoc_url: URL for ReDoc docs
        openapi_url: URL for OpenAPI schema
        swagger_ui_oauth2_redirect_url: OAuth2 redirect URL
        swagger_ui_parameters: Swagger UI parameters
    """
    # Update app properties
    app.title = title or f"{service_name.title()} API"
    app.description = description or f"Summiva {service_name.title()} Service API"
    app.version = version or getattr(settings, "API_VERSION", "1.0.0")
    
    # Set URLs
    app.docs_url = docs_url
    app.redoc_url = redoc_url
    app.openapi_url = openapi_url
    app.swagger_ui_oauth2_redirect_url = swagger_ui_oauth2_redirect_url
    
    # Set default Swagger UI parameters if not provided
    if swagger_ui_parameters is None:
        swagger_ui_parameters = {
            "docExpansion": "none",  # "list", "full", "none"
            "defaultModelsExpandDepth": 1,
            "defaultModelExpandDepth": 1,
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
        }
    
    app.swagger_ui_parameters = swagger_ui_parameters
    
    # Override OpenAPI schema generator
    def custom_openapi():
        return get_openapi_schema(
            app=app,
            service_name=service_name,
            title=app.title,
            description=app.description,
            version=app.version,
        )
    
    app.openapi = custom_openapi
    
    logger.info(f"Set up OpenAPI documentation for {service_name}")