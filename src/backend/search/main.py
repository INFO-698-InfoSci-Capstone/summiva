"""
Search Service Main Entry Point
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
from backend.search.api.search_api import router as search_router

def setup_routes(app):
    """Set up all route handlers for the search service"""
    app.include_router(search_router, prefix="/api/search", tags=["Search"])

async def startup_handler(app):
    """Additional startup tasks specific to search service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("search")
    logger.info("Initializing search indices and services...")
    # Add any search-specific initialization here
    # e.g., initialize Elasticsearch, FAISS indices, etc.

async def shutdown_handler(app):
    """Additional shutdown tasks specific to search service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("search")
    logger.info("Cleaning up search resources...")
    # Add any search-specific cleanup here

def create_app():
    """Create the FastAPI application for the search service"""
    return init_service(
        service_name="search",
        title="Document Search API",
        description="API for document search and retrieval using various search engines and vector databases",
        routes_setup=setup_routes,
        startup_handlers=[startup_handler],
        shutdown_handlers=[shutdown_handler]
    )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
