"""
Tagging Service Main Entry Point
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
from backend.tagging.api.tagging_api import router as tagging_router

def setup_routes(app):
    """Set up all route handlers for the tagging service"""
    app.include_router(tagging_router, prefix="/api/tagging", tags=["Tagging"])

async def startup_handler(app):
    """Additional startup tasks specific to tagging service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("tagging")
    logger.info("Initializing tagging models and services...")
    # Add any tagging-specific initialization here
    # e.g., load ML models, connect to specialized services, etc.

async def shutdown_handler(app):
    """Additional shutdown tasks specific to tagging service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("tagging")
    logger.info("Cleaning up tagging resources...")
    # Add any tagging-specific cleanup here

def create_app():
    """Create the FastAPI application for the tagging service"""
    return init_service(
        service_name="tagging",
        title="Document Tagging API",
        description="API for document tagging and classification using various ML models",
        routes_setup=setup_routes,
        startup_handlers=[startup_handler],
        shutdown_handlers=[shutdown_handler]
    )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
