
from backend.auth.api import auth_router
from backend.auth.config import settings
from fastapi import FastAPI


app = FastAPI(
    title="Auth Service",
    description="Authentication and authorization service for Summiva",
    version=settings.SERVICE_VERSION,
    debug=settings.DEBUG
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
