from src.backend.auth.api.endpoints.auth import router as auth_router
from config.settings.settings import settings
from fastapi import FastAPI, Response, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY


app = FastAPI(
    title="Auth Service",
    description="Authentication and authorization service for Summiva",
    version=settings.APP_SERVICE_VERSION,
    debug=settings.APP_DEBUG,
)

instrumentator = Instrumentator()
instrumentator.instrument(app)


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")
