"""
Base Schema Models
===============
Provides base Pydantic models for consistent API responses.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel as PydanticBaseModel, Field, validator
from pydantic.generics import GenericModel

from backend.core.imports import setup_imports
setup_imports()

# Type variable for generic models
T = TypeVar('T')
DataT = TypeVar('DataT')


class BaseConfig:
    """Configuration for all Pydantic models"""
    orm_mode = True
    allow_population_by_field_name = True
    validate_assignment = True
    json_encoders = {
        datetime: lambda dt: dt.isoformat()
    }
    

class BaseModel(PydanticBaseModel):
    """Base model for all schema models"""
    
    class Config(BaseConfig):
        pass
    
    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """Convert empty strings to None"""
        if v == '':
            return None
        return v


class ErrorResponse(BaseModel):
    """Standard error response model"""
    message: str = Field(..., description="Human-readable error message")
    type: str = Field(..., description="Error type identifier")
    detail: Dict[str, Any] = Field(default_factory=dict, description="Detailed error information")


class APIResponse(GenericModel, Generic[DataT]):
    """
    Standard API response wrapper
    
    This model ensures all API responses follow the same structure with:
    - success: Boolean flag indicating success/failure
    - data: Response data (generic type)
    - error: Error information (optional, present when success=False)
    - meta: Additional metadata (optional)
    """
    success: bool = Field(True, description="Success status")
    data: Optional[DataT] = Field(None, description="Response data")
    error: Optional[ErrorResponse] = Field(None, description="Error information")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config(BaseConfig):
        pass


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Standard paginated response model
    
    This model ensures all paginated API responses follow the same structure with:
    - items: List of items for current page
    - total: Total number of items across all pages
    - page: Current page number
    - size: Number of items per page
    - pages: Total number of pages
    """
    items: List[T] = Field([], description="List of items for current page")
    total: int = Field(..., ge=0, description="Total item count across all pages")
    page: int = Field(1, ge=1, description="Current page number")
    size: int = Field(..., ge=0, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    class Config(BaseConfig):
        pass
    
    @validator('pages', pre=False)
    def calculate_pages(cls, v, values):
        """Calculate total pages if not provided"""
        if v == 0 and 'total' in values and 'size' in values:
            total = values['total']
            size = values['size'] or 1  # Avoid division by zero
            return (total + size - 1) // size if size else 0
        return v