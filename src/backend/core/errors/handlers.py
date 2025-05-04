"""
Error Handlers
============
Standardized FastAPI error handlers for consistent error responses.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.imports import setup_imports
setup_imports()

from config.logs.logging import setup_logging
from backend.core.errors.exceptions import (
    AppError, 
    ValidationError,
    NotFoundError,
    AuthenticationError,
    AuthorizationError
)

# Get logger for this module
logger = setup_logging("core.errors")

def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """
    Handle custom application errors.
    
    Args:
        request: FastAPI request
        exc: AppError exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.error(f"Application error: {str(exc)}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "detail": exc.detail or {}
            }
        }
    )

def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: RequestValidationError exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.error(f"Validation error: {str(exc)}")
    
    # Format validation errors
    detail = {}
    for error in exc.errors():
        location = error.get("loc", [])
        if location:
            field = ".".join(str(loc) for loc in location if loc != "body")
            detail[field] = error.get("msg", "Invalid value")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "type": "ValidationError",
                "detail": detail
            }
        }
    )

def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: StarletteHTTPException exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.error(f"HTTP error {exc.status_code}: {str(exc.detail)}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": str(exc.detail),
                "type": "HTTPError",
                "detail": {}
            }
        }
    )

def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    """
    Handle "not found" errors.
    
    Args:
        request: FastAPI request
        exc: NotFoundError exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.warning(f"Resource not found: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "message": exc.message,
                "type": "NotFoundError",
                "detail": exc.detail or {}
            }
        }
    )

def handle_auth_error(request: Request, exc: AuthenticationError) -> JSONResponse:
    """
    Handle authentication errors.
    
    Args:
        request: FastAPI request
        exc: AuthenticationError exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.warning(f"Authentication error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": {
                "message": exc.message,
                "type": "AuthenticationError",
                "detail": exc.detail or {}
            }
        },
        headers={"WWW-Authenticate": "Bearer"}
    )

def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Any exception
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "type": "InternalError",
                "detail": {"info": str(exc)} if settings.DEBUG else {}
            }
        }
    )

def setup_error_handlers(app: FastAPI) -> None:
    """
    Configure standardized error handlers for a FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    from config.settings import settings
    
    # Register exception handlers
    app.exception_handler(AppError)(handle_app_error)
    app.exception_handler(RequestValidationError)(handle_validation_error)
    app.exception_handler(StarletteHTTPException)(handle_http_error)
    app.exception_handler(NotFoundError)(handle_not_found_error)
    app.exception_handler(AuthenticationError)(handle_auth_error)
    app.exception_handler(Exception)(handle_generic_error)
    
    logger.info("Registered standardized error handlers")