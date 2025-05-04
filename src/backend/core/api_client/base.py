"""
Base API Client
=============
Base client class for service-to-service communication.
"""
from typing import Any, Dict, Optional, Type, TypeVar, Union, Generic, List
import json
import logging
import httpx
from pydantic import parse_obj_as

from backend.core.imports import setup_imports
setup_imports()

from backend.core.schemas.base import APIResponse, BaseModel
from backend.core.errors.exceptions import (
    AppError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError
)
from config.logs.logging import setup_logging

# Get logger for this module
logger = setup_logging("core.api_client")

# Type variable for response data
T = TypeVar('T')

class BaseAPIClient:
    """
    Base client for making API requests to other services
    
    This class handles:
    - Standard request/response formatting
    - Authentication token management
    - Error handling and mapping
    - Timeouts and retries
    """
    
    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        auth_token: Optional[str] = None
    ):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for the service API
            service_name: Service name for logging
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            auth_token: Optional authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.auth_token = auth_token
        
        # Initialize HTTP client with timeouts
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True
        )
        
        logger.info(f"Initialized API client for {service_name} at {base_url}")
    
    async def close(self):
        """Close the HTTP client session"""
        await self.client.aclose()
        logger.debug(f"Closed API client for {self.service_name}")
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build request headers
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            Dict[str, str]: Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Service-Name": self.service_name
        }
        
        # Add auth token if available
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            str: Full URL
        """
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]) -> None:
        """
        Handle error responses by raising appropriate exceptions
        
        Args:
            status_code: HTTP status code
            response_data: Response data
            
        Raises:
            Various exceptions based on status code
        """
        # Extract error details if available
        message = "Unknown error"
        detail = {}
        
        # Try to extract error message from different response formats
        if isinstance(response_data, dict):
            if "error" in response_data and isinstance(response_data["error"], dict):
                error_data = response_data["error"]
                message = error_data.get("message", message)
                detail = error_data.get("detail", {})
            elif "message" in response_data:
                message = response_data["message"]
            elif "detail" in response_data:
                message = str(response_data["detail"])
        
        # Map status codes to appropriate exceptions
        if status_code == 400:
            raise ValidationError(message=message, detail=detail)
        elif status_code == 401:
            raise AuthenticationError(message=message, detail=detail)
        elif status_code == 403:
            raise AuthorizationError(message=message, detail=detail)
        elif status_code == 404:
            raise NotFoundError(message=message, detail=detail)
        elif status_code == 422:
            raise ValidationError(message=message, detail=detail)
        elif status_code >= 500:
            raise ServiceUnavailableError(
                message=f"{self.service_name} service error: {message}",
                detail=detail
            )
        else:
            raise AppError(message=message, status_code=status_code, detail=detail)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make HTTP request with retries and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
            
        Raises:
            AppError: For API errors
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(headers)
        
        # Convert data to JSON if provided
        json_data = None
        if data is not None:
            # Handle Pydantic models
            if isinstance(data, BaseModel):
                json_data = data.dict(exclude_unset=True)
            else:
                json_data = data
        
        # Perform request with retries
        attempts = 0
        last_error = None
        
        while attempts < self.max_retries:
            attempts += 1
            
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempts}/{self.max_retries})")
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=headers
                )
                
                # Try to parse response as JSON
                try:
                    response_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    if response.content:
                        response_data = {"content": response.text}
                    else:
                        response_data = {}
                
                # Check status code
                if response.is_success:
                    # Parse response data
                    if response_model:
                        # Handle wrapped responses (APIResponse)
                        if wrap_response and isinstance(response_data, dict) and "data" in response_data:
                            result_data = response_data["data"]
                            return parse_obj_as(response_model, result_data)
                        else:
                            return parse_obj_as(response_model, response_data)
                    else:
                        # Return raw response data
                        if wrap_response and isinstance(response_data, dict) and "data" in response_data:
                            return response_data["data"]
                        else:
                            return response_data
                else:
                    # Handle error based on status code
                    self._handle_error_response(response.status_code, response_data)
                    
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout) as e:
                last_error = e
                logger.warning(f"Connection error during {method} request to {url}: {str(e)}")
                
                # If we've reached max retries, raise exception
                if attempts >= self.max_retries:
                    raise ServiceUnavailableError(
                        message=f"Failed to connect to {self.service_name} service after {self.max_retries} attempts",
                        detail={"error": str(e)}
                    )
                
                continue  # Retry
            
            except (AppError, Exception) as e:
                # Don't retry for API errors or other exceptions
                raise
        
        # Should not reach here, but just in case
        if last_error:
            raise ServiceUnavailableError(
                message=f"Failed to connect to {self.service_name} service",
                detail={"error": str(last_error)}
            )
        else:
            raise AppError(message=f"Unknown error communicating with {self.service_name} service")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make GET request
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
        """
        return await self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
            response_model=response_model,
            wrap_response=wrap_response
        )
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make POST request
        
        Args:
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
        """
        return await self._make_request(
            method="POST",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            response_model=response_model,
            wrap_response=wrap_response
        )
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make PUT request
        
        Args:
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
        """
        return await self._make_request(
            method="PUT",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            response_model=response_model,
            wrap_response=wrap_response
        )
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make PATCH request
        
        Args:
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
        """
        return await self._make_request(
            method="PATCH",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            response_model=response_model,
            wrap_response=wrap_response
        )
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
        wrap_response: bool = True
    ) -> Union[T, Dict[str, Any], List[Any]]:
        """
        Make DELETE request
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model for response parsing
            wrap_response: Whether response is wrapped in APIResponse
            
        Returns:
            Parsed response data
        """
        return await self._make_request(
            method="DELETE",
            endpoint=endpoint,
            params=params,
            headers=headers,
            response_model=response_model,
            wrap_response=wrap_response
        )