import os
from backend.auth.api import auth_api
from backend.grouping.api import grouping_api
from backend.search.api import search_api
from backend.summarization.api import summarization_api
from config.logs.logging import setup_logging
from backend.tagging.api import tagging_api
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY

from src.backend.core.config.settings import settings
from src.backend.core.middleware.middleware import setup_middleware
from src.backend.core.database.database import init_db, engine, Base

import logging

# -----------------------
# Logging Configuration
# -----------------------
setup_logging()

# -----------------------
# App Initialization
# -----------------------
app = FastAPI(
    title="Document Grouping API",
    description="API for grouping documents using various algorithms",
    version="1.0.0"
)

instrumentator = Instrumentator()

# -----------------------
# Middleware Setup
# -----------------------
setup_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# -----------------------
# Database Initialization
# -----------------------
@app.on_event("startup")
async def startup_event():
    init_db()
    Base.metadata.create_all(bind=engine)
    instrumentator.instrument(app)

# -----------------------
# Routes
# -----------------------
# Core routes
@app.get("/")
async def root():
    return {"message": "Document Grouping API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")

# Feature routers
app.include_router(auth_api, prefix="/api/auth", tags=["auth"])
app.include_router(summarization_api, prefix="/api/summarization", tags=["summarization"])
app.include_router(tagging_api, prefix="/api/tagging", tags=["tagging"])
app.include_router(search_api, prefix="/api/search", tags=["search"])
app.include_router(grouping_api, prefix="/api/grouping", tags=["grouping"])
