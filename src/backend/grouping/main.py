"""
Grouping Service Main Entry Point
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
from backend.grouping.api.grouping_api import router as grouping_router

def setup_routes(app):
    """Set up all route handlers for the grouping service"""
    app.include_router(grouping_router, prefix="/api/grouping", tags=["Grouping"])

async def startup_handler(app):
    """Additional startup tasks specific to grouping service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("grouping")
    logger.info("Initializing document grouping models...")
    # Add any grouping-specific initialization here
    # e.g., load clustering algorithms, initialize vector spaces, etc.

async def shutdown_handler(app):
    """Additional shutdown tasks specific to grouping service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("grouping")
    logger.info("Cleaning up grouping resources...")
    # Add any grouping-specific cleanup here

def create_app():
    """Create the FastAPI application for the grouping service"""
    return init_service(
        service_name="grouping",
        title="Document Grouping API",
        description="API for document clustering and grouping using various algorithms",
        routes_setup=setup_routes,
        startup_handlers=[startup_handler],
        shutdown_handlers=[shutdown_handler]
    )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
