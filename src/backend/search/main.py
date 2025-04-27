from fastapi import FastAPI
from .config.settings import settings
from .database.connection import get_db, get_es
from .api import search_router

app = FastAPI(
    title="Search Service",
    description="Search service for Summiva",
    version=settings.SERVICE_VERSION,
    debug=settings.DEBUG
)

# Include routers
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
