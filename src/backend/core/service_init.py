# Service initialization helper
"""
Helper module to standardize service initialization across all Summiva services.
"""

from fastapi import FastAPI
from typing import Optional, Dict, Any, List, Callable, Union

from backend.core.imports import setup_imports
setup_imports()

from backend.core.middleware.core_middleware import setup_middlewares
from backend.core.errors.handlers import setup_error_handlers
from backend.core.docs.openapi import setup_openapi
from config.logs.logging import setup_logging
from backend.core.database.database import init_db, engine, Base

def init_service(
    service_name: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    middleware_options: Optional[Dict[str, Any]] = None,
    routes_setup: Optional[Callable] = None,
    startup_handlers: Optional[List[Callable]] = None,
    shutdown_handlers: Optional[List[Callable]] = None,
    enable_error_handlers: bool = True,
    enable_openapi: bool = True,
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
) -> FastAPI:
    """
    Initialize a service with standardized settings and configurations.
    
    Args:
        service_name: The name of the service (e.g., 'auth', 'summarization')
        title: API title (defaults to '{service_name} Service')
        description: API description (defaults to standard template)
        version: API version (defaults to settings.APP_SERVICE_VERSION)
        middleware_options: Custom middleware options
        routes_setup: Function to set up routes
        startup_handlers: List of additional startup event handlers
        shutdown_handlers: List of additional shutdown event handlers
        enable_error_handlers: Whether to enable standardized error handlers
        enable_openapi: Whether to set up standardized OpenAPI documentation
        docs_url: URL for API documentation
        redoc_url: URL for ReDoc documentation
    
    Returns:
        Configured FastAPI application
    """
    from config.settings import settings
    
    # Configure logger first
    logger = setup_logging(service_name)
    
    # Set defaults
    title = title or f"{service_name.capitalize()} Service"
    description = description or f"Summiva {service_name.capitalize()} Service API"
    version = version or getattr(settings, "APP_SERVICE_VERSION", "1.0.0")
    
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
    )
    
    # Set up middleware
    middleware_options = middleware_options or {}
    setup_middlewares(app, **middleware_options)
    
    # Set up error handlers if enabled
    if enable_error_handlers:
        setup_error_handlers(app)
        
    # Set up OpenAPI documentation if enabled
    if enable_openapi:
        setup_openapi(
            app=app,
            service_name=service_name,
            title=title,
            description=description,
            version=version,
            docs_url=docs_url,
            redoc_url=redoc_url
        )
    
    # Standard startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {service_name} service")
        # Initialize database
        init_db()
        Base.metadata.create_all(bind=engine)
        
        # Run additional startup handlers
        if startup_handlers:
            for handler in startup_handlers:
                await handler(app)
    
    # Standard shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {service_name} service")
        
        # Close database connections
        from backend.core.database.mongo_db import close_mongo_connections
        from backend.core.database.redis_db import close_redis_connection
        from backend.core.api_client.factory import close_all_clients
        
        # Close all database connections
        try:
            close_mongo_connections()
        except Exception as e:
            logger.error(f"Error closing MongoDB connections: {str(e)}")
            
        try:
            close_redis_connection()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")
        
        # Close all API clients
        try:
            await close_all_clients()
        except Exception as e:
            logger.error(f"Error closing API clients: {str(e)}")
        
        # Run additional shutdown handlers
        if shutdown_handlers:
            for handler in shutdown_handlers:
                await handler(app)
    
    # Set up routes if provided
    if routes_setup:
        routes_setup(app)
    
    # Standard health check endpoint
    @app.get("/health", tags=["System"])
    async def health_check():
        """Service health check endpoint"""
        return {"status": "healthy", "service": service_name}
    
    return app