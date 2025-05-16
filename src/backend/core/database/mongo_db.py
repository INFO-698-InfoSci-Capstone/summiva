"""
MongoDB Connection Module
=========================
Provides standardized MongoDB connections for all services that use document storage.
"""

import logging
from typing import Optional
from config.logging.logging import setup_logging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from src.backend.core.imports import setup_imports
setup_imports()

from config.settings import settings

# Get logger for this module
logger = setup_logging("core.database.mongodb")

# Global client and db instance
_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[Database] = None

def get_mongo_client() -> MongoClient:
    """
    Lazily initializes and returns a MongoDB client.

    Returns:
        MongoClient: MongoDB client instance
    """
    global _mongo_client

    if _mongo_client is None:
        mongo_url = getattr(settings, "MONGODB_URL", None)

        # If full MongoDB URL is not provided, construct it from parts
        if not mongo_url:
            mongo_host = getattr(settings, "MONGODB_HOST", "localhost")
            mongo_port = getattr(settings, "MONGODB_PORT", 27017)
            mongo_user = getattr(settings, "MONGODB_USER", "")
            mongo_pass = getattr(settings, "MONGODB_PASSWORD", "")

            if mongo_user and mongo_pass:
                mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
            else:
                mongo_url = f"mongodb://{mongo_host}:{mongo_port}"

            logger.info(f"Connecting to MongoDB at {mongo_host}:{mongo_port}")
        else:
            logger.info("Connecting to MongoDB using MONGODB_URL")

        try:
            _mongo_client = MongoClient(mongo_url)
            _mongo_client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    return _mongo_client

def get_mongo_db() -> Database:
    """
    Returns a handle to the MongoDB database specified in settings.

    Returns:
        Database: MongoDB database instance
    """
    global _mongo_db

    if _mongo_db is None:
        client = get_mongo_client()
        db_name = getattr(settings, "MONGODB_DB", "summiva")
        _mongo_db = client[db_name]
        logger.info(f"Using MongoDB database: {db_name}")

    return _mongo_db

def close_mongo_connections():
    """
    Cleanly closes MongoDB connections if they are open.
    """
    global _mongo_client, _mongo_db

    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB connections closed")

    _mongo_client = None
    _mongo_db = None

# FastAPI Dependency
def get_db_mongo():
    """
    FastAPI Dependency for injecting MongoDB database.

    Example usage:
        @app.get("/items/")
        def read_items(db: Database = Depends(get_db_mongo)):
            return list(db.items.find())
    """
    db = get_mongo_db()
    try:
        yield db
    finally:
        # Shared client, nothing to close per request
        pass