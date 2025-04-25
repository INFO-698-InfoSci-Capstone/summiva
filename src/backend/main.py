from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from core.config.settings import settings
from src.backend.core.middleware.middleware import setup_middleware
from src.backend.core.database.database import init_db, engine, Base
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Document Grouping API",
    description="API for grouping documents using various algorithms",
    version="1.0.0"
)

instrumentator = Instrumentator()


# Setup middleware
setup_middleware(app)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    # Create database tables
    Base.metadata.create_all(bind=engine)
    instrumentator.instrument(app)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers
from src.apps.auth.routes.auth_routes import router as auth_router
from src.apps.summarization.routes.summarization_routes import router as summarization_router
from src.apps.tagging.routes.tagging_routes import router as tagging_router
from src.apps.search.routes.search_routes import router as search_router
from src.apps.grouping.routes.grouping_routes import router as grouping_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(summarization_router, prefix="/api/summarization", tags=["summarization"])
app.include_router(tagging_router, prefix="/api/tagging", tags=["tagging"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(grouping_router, prefix="/api/grouping", tags=["grouping"])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")


@app.get("/")
async def root():
    return {"message": "Document Grouping API is running"}
