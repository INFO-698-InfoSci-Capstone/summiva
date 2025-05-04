"""
Summarization Service Main Entry Point
=====================================
"""
import asyncio
from pathlib import Path
import sys

# Add project root to path to ensure imports work correctly
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.core.imports import setup_imports
setup_imports()

from backend.core.service_init import init_service
from backend.summarization.api.summarization_api import router as summarization_router

def setup_routes(app):
    """Set up all route handlers for the summarization service"""
    app.include_router(summarization_router, prefix="/api/summarization", tags=["Summarization"])

async def startup_handler(app):
    """Additional startup tasks specific to summarization service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("summarization")
    logger.info("Initializing summarization models...")
    # Add any summarization-specific initialization here
    # e.g., load ML models, connect to specialized services, etc.

async def shutdown_handler(app):
    """Additional shutdown tasks specific to summarization service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("summarization")
    logger.info("Cleaning up summarization resources...")
    # Add any summarization-specific cleanup here

def create_app():
    """Create the FastAPI application for the summarization service"""
    return init_service(
        service_name="summarization",
        title="Document Summarization API",
        description="API for document summarization using various NLP models",
        routes_setup=setup_routes,
        startup_handlers=[startup_handler],
        shutdown_handlers=[shutdown_handler]
    )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
