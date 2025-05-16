"""
Redis Connection Module
=====================
Provides standardized Redis connections for all services that use caching or messaging.
"""
import logging
from typing import Optional, Dict, Any, Union
import json
from config.logging.logging import setup_logging
import redis
from redis import Redis

from src.backend.core.imports import setup_imports
setup_imports()

from config.settings import settings

# Get logger for this module
logger = setup_logging("core.database.redis")

# Global Redis client instance
_redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    """
    Get or initialize the Redis client.
    
    Returns:
        Redis: Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        # Get Redis connection parameters from settings
        redis_url = getattr(settings, "REDIS_URL", None)
        if not redis_url:            # Construct from parts if full URL not provided
            redis_host = getattr(settings, "REDIS_HOST", "localhost")
            redis_port = getattr(settings, "REDIS_PORT", 6379)
            redis_db = getattr(settings, "REDIS_DB", 0)
            redis_password = getattr(settings, "REDIS_PASSWORD", "summiva_redis_password")
            
            logger.info(f"Connecting to Redis at {redis_host}:{redis_port}/{redis_db}")
            
            _redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                ssl=getattr(settings, "REDIS_USE_SSL", False)
            )
        else:
            logger.info(f"Connecting to Redis using URL: {redis_url}")
            _redis_client = redis.from_url(
                redis_url, 
                decode_responses=True, 
                socket_timeout=5,
                socket_connect_timeout=5
            )
        
        try:
            # Test connection
            _redis_client.ping()
            logger.info("Successfully connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    return _redis_client

def close_redis_connection():
    """Close the Redis connection"""
    global _redis_client
    
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
        logger.info("Closed Redis connection")

# Convenience methods for working with Redis

def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set a value in the Redis cache with TTL.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized if not a string)
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        bool: Success status
    """
    client = get_redis_client()
    
    if not isinstance(value, str):
        value = json.dumps(value)
    
    return client.setex(key, ttl, value)

def cache_get(key: str, default: Any = None) -> Any:
    """
    Get a value from the Redis cache.
    
    Args:
        key: Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    client = get_redis_client()
    value = client.get(key)
    
    if value is None:
        return default
        
    try:
        # Try to parse as JSON
        return json.loads(value)
    except json.JSONDecodeError:
        # Return as string if not JSON
        return value

def cache_delete(key: str) -> int:
    """
    Delete a key from the Redis cache.
    
    Args:
        key: Cache key
        
    Returns:
        int: Number of keys deleted
    """
    client = get_redis_client()
    return client.delete(key)

# For dependency injection in FastAPI
def get_redis():
    """
    Dependency for getting Redis client
    
    Usage in FastAPI:
        @app.get("/items/{item_id}")
        def get_item(item_id: str, redis: Redis = Depends(get_redis)):
            cached = redis.get(f"item:{item_id}")
            if cached:
                return json.loads(cached)
            # ...fetch from database if not cached
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        # Nothing to explicitly close per request, client is shared
        pass