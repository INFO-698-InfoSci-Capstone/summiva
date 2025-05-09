"""
Moderation Service Main Entry Point
=====================================
Content moderation service to filter inappropriate content using 
better-profanity and Jigsaw Toxicity BERT models.
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
from backend.moderation.api.moderation_api import router as moderation_router

def setup_routes(app):
    """Set up all route handlers for the moderation service"""
    app.include_router(moderation_router, prefix="/api/moderation", tags=["Moderation"])

async def startup_handler(app):
    """Additional startup tasks specific to moderation service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("moderation")
    logger.info("Initializing moderation models and filters...")
    
    # Initialize moderation models and filters
    from backend.moderation.services.moderation_service import ModerationService
    await ModerationService.initialize()

async def shutdown_handler(app):
    """Additional shutdown tasks specific to moderation service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("moderation")
    logger.info("Cleaning up moderation resources...")
    
    # Clean up moderation resources
    from backend.moderation.services.moderation_service import ModerationService
    await ModerationService.cleanup()

def create_app():
    """Create the FastAPI application for the moderation service"""
    return init_service(
        service_name="moderation",
        title="Content Moderation API",
        description="API for content moderation, profanity filtering, and toxic content detection",
        routes_setup=setup_routes,
        startup_handlers=[startup_handler],
        shutdown_handlers=[shutdown_handler]
    )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)