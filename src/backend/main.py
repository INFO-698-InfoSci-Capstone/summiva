# -----------------------
# Standard Library
# -----------------------
import os
import sys
from pathlib import Path
from logging import config as logging_config
import importlib

# -----------------------
# Setup Python Path
# -----------------------
# Add project root to sys.path to enable absolute imports
project_root = Path(__file__).parent.parent.parent
config_dir = project_root / 'config'
settings_dir = config_dir / 'settings'

# Add all necessary paths to sys.path
for path in [str(project_root), str(config_dir), str(settings_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Ensure config is a proper package
init_file = config_dir / '__init__.py'
if not init_file.exists():
    try:
        init_file.touch()
        print(f"Created __init__.py in {config_dir}")
    except Exception as e:
        print(f"Warning: Could not create __init__.py in {config_dir}: {str(e)}")

# Ensure settings is a proper package
init_file = settings_dir / '__init__.py'
if not init_file.exists():
    try:
        init_file.touch()
        print(f"Created __init__.py in {settings_dir}")
    except Exception as e:
        print(f"Warning: Could not create __init__.py in {settings_dir}: {str(e)}")

# -----------------------
# Import Setup
# -----------------------
try:
    from src.backend.core.imports import setup_imports
    # Configure import paths first before any other imports
    setup_imports()
except ImportError:
    print(f"Failed to import setup_imports. Current sys.path: {sys.path}")
    raise

# -----------------------
# Third-Party Libraries
# -----------------------
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY

# -----------------------
# Internal Modules
# -----------------------
# Try to import settings using different methods
try:
    from config.settings import settings
except ImportError:
    try:
        # Try direct import
        sys.path.insert(0, str(settings_dir))
        from settings import settings
    except ImportError as e:
        print(f"Warning: Could not import settings: {str(e)}. Using environment variables.")
        # Create a fallback settings class using env vars
        class DefaultSettings:
            def __init__(self):
                self.APP_NAME = os.environ.get("APP_NAME", "Summiva")
                self.APP_SERVICE_VERSION = os.environ.get("APP_SERVICE_VERSION", "1.0.0")
                self.CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
                self.CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "True") == "True"
                self.CORS_ALLOW_METHODS = ["*"]
                self.CORS_ALLOW_HEADERS = ["*"]
                
        settings = DefaultSettings()

from config.logs.logging import setup_logging
from src.backend.core.message_queue import MessageQueue
from src.backend.core.service_registry import ServiceRegistry
from src.backend.auth.api import auth_api
from src.backend.search.api import search_api
from src.backend.tagging.api import tagging_api
from src.backend.grouping.api import grouping_api
from src.backend.summarization.api import summarization_api
from src.backend.core.middleware.core_middleware import setup_middlewares
from src.backend.core.database.database import init_db, engine, Base

# -----------------------
# Logging Configuration
# -----------------------
logger = setup_logging()
logger.info(f"Starting application with sys.path: {sys.path}")

# -----------------------
# App Initialization
# -----------------------
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description=f"Enterprise-scale NLP system for content summarization, tagging, grouping, and search",
    version=settings.APP_SERVICE_VERSION,
)

instrumentator = Instrumentator()

# -----------------------
# Middleware Setup
# -----------------------
setup_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# -----------------------
# Database & Service Startup
# -----------------------
@app.on_event("startup")
async def startup_event():
    init_db()
    Base.metadata.create_all(bind=engine)
    instrumentator.instrument(app)

    db_url = os.getenv('DATABASE_URL')
    if db_url:
        logging_config.set_main_option('sqlalchemy.url', db_url)

    # Initialize and check services at startup
    service_registry = ServiceRegistry()
    healthy_services = await service_registry.discover_services()
    if not healthy_services:
        logger.warning("No healthy services detected at startup.")
    else:
        logger.info(f"Healthy services at startup: {list(healthy_services.keys())}")
    
    # Connect to Message Queue
    global message_queue
    message_queue = MessageQueue()
    await message_queue.connect()
    logger.info("MessageQueue connected at startup.")

# -----------------------
# Core Routes
# -----------------------
@app.get("/", tags=["System"])
async def root():
    return {"message": "Document Grouping API is running"}

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics", tags=["System"])
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")

# -----------------------
# Feature Routers
# -----------------------
app.include_router(auth_api, prefix="/api/auth", tags=["Auth"])
app.include_router(summarization_api, prefix="/api/summarization", tags=["Summarization"])
app.include_router(tagging_api, prefix="/api/tagging", tags=["Tagging"])
app.include_router(search_api, prefix="/api/search", tags=["Search"])
app.include_router(grouping_api, prefix="/api/grouping", tags=["Grouping"])

# -----------------------
# Shutdown Event
# -----------------------
@app.on_event("shutdown")
async def shutdown_event():
    # Disconnect from Message Queue
    global message_queue
    if message_queue:
        await message_queue.close()
        logger.info("MessageQueue disconnected at shutdown.")