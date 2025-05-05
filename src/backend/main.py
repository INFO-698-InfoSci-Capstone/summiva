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
sys.path.insert(0, str(project_root))

# Import settings module with configurable precedence
try:
    from config.settings import settings
except ImportError:
    try:
        from config.settings.settings import settings
    except ImportError:
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

# -----------------------
# Third-Party Libraries
# -----------------------
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import generate_latest, REGISTRY

# -----------------------
# Internal Modules
# -----------------------
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
logger.info(f"Starting {settings.APP_NAME} service")

# -----------------------
# App Initialization
# -----------------------
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description=f"Enterprise-scale NLP system for content summarization, tagging, grouping, and search",
    version=settings.APP_SERVICE_VERSION,
)

# Setup Prometheus instrumentation with extended metrics
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
)

# Add custom metrics
instrumentator.add(
    metrics.latency(
        should_include_method=True,
        should_include_status=True,
        should_include_handler=True,
    )
)
instrumentator.add(metrics.requests())
instrumentator.add(metrics.cpu_percent())
instrumentator.add(metrics.memory_usage())

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
    logger.info("Service starting up...")
    
    # Initialize database
    try:
        init_db()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
    
    # Initialize monitoring
    instrumentator.instrument(app)
    logger.info("Metrics instrumentation set up")

    # Set database URL for logging configuration if available
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        logging_config.set_main_option('sqlalchemy.url', db_url)

    # Initialize and check services at startup
    try:
        service_registry = ServiceRegistry()
        healthy_services = await service_registry.discover_services()
        if not healthy_services:
            logger.warning("No healthy services detected at startup.")
        else:
            logger.info(f"Healthy services at startup: {list(healthy_services.keys())}")
    except Exception as e:
        logger.error(f"Service registry initialization error: {str(e)}")
    
    # Connect to Message Queue
    try:
        global message_queue
        message_queue = MessageQueue()
        await message_queue.connect()
        logger.info("MessageQueue connected at startup.")
    except Exception as e:
        logger.error(f"MessageQueue connection error: {str(e)}")

# -----------------------
# Core Routes
# -----------------------
@app.get("/", tags=["System"])
async def root():
    return {"message": f"{settings.APP_NAME} API is running", "version": settings.APP_SERVICE_VERSION}

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

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
    logger.info("Service shutting down...")
    
    # Disconnect from Message Queue
    try:
        global message_queue
        if message_queue:
            await message_queue.close()
            logger.info("MessageQueue disconnected at shutdown.")
    except Exception as e:
        logger.error(f"Error during MessageQueue disconnect: {str(e)}")