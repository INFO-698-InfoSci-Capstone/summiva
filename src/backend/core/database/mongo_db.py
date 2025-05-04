"""
MongoDB Connection Module
=======================
Provides standardized MongoDB connections for all services that use document storage.
"""
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from backend.core.imports import setup_imports
setup_imports()

from config.settings import settings
from config.logs.logging import setup_logging

# Get logger for this module
logger = setup_logging("core.database.mongodb")

# Global client instance
_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[Database] = None

def get_mongo_client() -> MongoClient:
    """
    Get or initialize the MongoDB client.
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _mongo_client
    
    if _mongo_client is None:
        # Get MongoDB connection parameters from settings
        mongo_url = getattr(settings, "MONGODB_URL", None)
        if not mongo_url:
            # Construct from parts if full URL not provided
            mongo_host = getattr(settings, "MONGODB_HOST", "localhost")
            mongo_port = getattr(settings, "MONGODB_PORT", 27017)
            mongo_user = getattr(settings, "MONGODB_USER", "")
            mongo_pass = getattr(settings, "MONGODB_PASSWORD", "")
            
            # Build connection string
            if mongo_user and mongo_pass:
                mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
            else:
                mongo_url = f"mongodb://{mongo_host}:{mongo_port}"
        
        logger.info(f"Connecting to MongoDB at {mongo_host}:{mongo_port}")
        
        try:
            _mongo_client = MongoClient(mongo_url)
            # Ping the server to verify connection
            _mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return _mongo_client

def get_mongo_db() -> Database:
    """
    Get the MongoDB database instance.
    
    Returns:
        Database: MongoDB database instance
    """
    global _mongo_db
    
    if _mongo_db is None:
        client = get_mongo_client()
        db_name = getattr(settings, "MONGODB_DB", "summiva")
        _mongo_db = client[db_name]
        logger.info(f"Connected to MongoDB database: {db_name}")
    
    return _mongo_db

def close_mongo_connections():
    """Close all MongoDB connections"""
    global _mongo_client, _mongo_db
    
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        logger.info("Closed MongoDB connections")

# For dependency injection in FastAPI
def get_db_mongo():
    """
    Dependency for getting MongoDB database handle
    
    Usage in FastAPI:
        @app.get("/items/")
        def get_items(db: Database = Depends(get_db_mongo)):
            items = db.items.find()
            return list(items)
    """
    db = get_mongo_db()
    try:
        yield db
    finally:
        # Nothing to explicitly close per request, client is shared
        pass