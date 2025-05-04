"""
API Client Factory
===============
Factory methods for creating service clients.
"""
from typing import Optional, Dict, Type, Any

from backend.core.imports import setup_imports
setup_imports()

from config.settings import settings
from backend.core.api_client.base import BaseAPIClient


# Registry of service client classes
_client_registry: Dict[str, Type[BaseAPIClient]] = {}

# Cached client instances
_client_instances: Dict[str, BaseAPIClient] = {}


def register_client_class(service_name: str, client_class: Type[BaseAPIClient]) -> None:
    """
    Register a client class for a service
    
    Args:
        service_name: Name of the service
        client_class: Client class for the service
    """
    _client_registry[service_name] = client_class


def get_service_client(
    service_name: str,
    base_url: Optional[str] = None,
    auth_token: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    use_cached: bool = True,
) -> BaseAPIClient:
    """
    Get a client for a service
    
    Args:
        service_name: Name of the service
        base_url: Override base URL for the service
        auth_token: Authentication token
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        use_cached: Whether to use cached client instances
        
    Returns:
        BaseAPIClient: Client for the requested service
        
    Raises:
        ValueError: If service is not registered
    """
    # Check if we should use a cached instance
    cache_key = f"{service_name}:{base_url or ''}:{auth_token or ''}"
    if use_cached and cache_key in _client_instances:
        return _client_instances[cache_key]
    
    # Get client class
    client_class = _client_registry.get(service_name)
    if not client_class:
        # Use base client if no specific client is registered
        client_class = BaseAPIClient
    
    # Determine base URL
    if not base_url:
        # Try to get from settings
        url_setting_name = f"{service_name.upper()}_SERVICE_URL"
        base_url = getattr(settings, url_setting_name, None)
        
        if not base_url:
            # Build from service name and base domain
            service_domain = getattr(
                settings, 
                "SERVICE_DOMAIN", 
                "localhost"
            )
            service_port = getattr(
                settings, 
                f"{service_name.upper()}_SERVICE_PORT", 
                None
            )
            
            if service_port:
                base_url = f"http://{service_name}.{service_domain}:{service_port}"
            else:
                base_url = f"http://{service_name}.{service_domain}"
    
    # Create client
    client = client_class(
        base_url=base_url,
        service_name=service_name,
        timeout=timeout or getattr(settings, "API_CLIENT_TIMEOUT", 10.0),
        max_retries=max_retries or getattr(settings, "API_CLIENT_MAX_RETRIES", 3),
        auth_token=auth_token
    )
    
    # Cache the client
    if use_cached:
        _client_instances[cache_key] = client
    
    return client


# Convenience functions for specific services
def get_auth_client(
    auth_token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseAPIClient:
    """
    Get auth service client
    
    Args:
        auth_token: Authentication token
        base_url: Override base URL for the service
        **kwargs: Additional client options
        
    Returns:
        BaseAPIClient: Auth service client
    """
    return get_service_client("auth", base_url=base_url, auth_token=auth_token, **kwargs)


def get_summarization_client(
    auth_token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseAPIClient:
    """
    Get summarization service client
    
    Args:
        auth_token: Authentication token
        base_url: Override base URL for the service
        **kwargs: Additional client options
        
    Returns:
        BaseAPIClient: Summarization service client
    """
    return get_service_client("summarization", base_url=base_url, auth_token=auth_token, **kwargs)


def get_search_client(
    auth_token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseAPIClient:
    """
    Get search service client
    
    Args:
        auth_token: Authentication token
        base_url: Override base URL for the service
        **kwargs: Additional client options
        
    Returns:
        BaseAPIClient: Search service client
    """
    return get_service_client("search", base_url=base_url, auth_token=auth_token, **kwargs)


def get_tagging_client(
    auth_token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseAPIClient:
    """
    Get tagging service client
    
    Args:
        auth_token: Authentication token
        base_url: Override base URL for the service
        **kwargs: Additional client options
        
    Returns:
        BaseAPIClient: Tagging service client
    """
    return get_service_client("tagging", base_url=base_url, auth_token=auth_token, **kwargs)


def get_grouping_client(
    auth_token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseAPIClient:
    """
    Get grouping service client
    
    Args:
        auth_token: Authentication token
        base_url: Override base URL for the service
        **kwargs: Additional client options
        
    Returns:
        BaseAPIClient: Grouping service client
    """
    return get_service_client("grouping", base_url=base_url, auth_token=auth_token, **kwargs)


async def close_all_clients() -> None:
    """Close all cached client instances"""
    for client in _client_instances.values():
        await client.close()
    _client_instances.clear()