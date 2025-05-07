"""
Core Database Module
==================
Provides database utilities and session management for all services.
"""

from src.backend.core.imports import setup_imports
setup_imports()

# PostgreSQL / SQLAlchemy
from backend.core.database.database import (
    get_db,
    init_db,
    engine,
    Base,
    SessionLocal
)

# MongoDB
from backend.core.database.mongo_db import (
    get_mongo_client,
    get_mongo_db,
    get_db_mongo,
    close_mongo_connections
)

# Redis
from backend.core.database.redis_db import (
    get_redis_client,
    get_redis,
    cache_get,
    cache_set,
    cache_delete,
    close_redis_connection
)

__all__ = [
    # PostgreSQL / SQLAlchemy
    'get_db', 'init_db', 'engine', 'Base', 'SessionLocal',
    # MongoDB
    'get_mongo_client', 'get_mongo_db', 'get_db_mongo', 'close_mongo_connections',
    # Redis
    'get_redis_client', 'get_redis', 'cache_get', 'cache_set', 'cache_delete', 'close_redis_connection'
]