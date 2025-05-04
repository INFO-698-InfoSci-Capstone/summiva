"""
Pagination Schema Models
======================
Provides standardized pagination models for consistent API request handling.
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, validator

from backend.core.imports import setup_imports
setup_imports()

from backend.core.schemas.base import BaseModel, BaseConfig


class SortDirection(str, Enum):
    """Sort direction enum"""
    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """
    Sorting parameters
    
    Attributes:
        field: Field to sort by
        direction: Sort direction (asc or desc)
    """
    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")
    
    class Config(BaseConfig):
        pass


class PageParams(BaseModel):
    """
    Pagination request parameters
    
    Attributes:
        page: Page number (1-indexed)
        size: Number of items per page
        sort: Optional sorting parameters
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(10, ge=1, le=100, description="Items per page")
    sort: Optional[List[SortParams]] = Field(None, description="Sorting parameters")
    
    class Config(BaseConfig):
        pass
    
    def get_skip(self) -> int:
        """
        Calculate number of records to skip
        
        Returns:
            int: Number of records to skip
        """
        return (self.page - 1) * self.size
    
    def get_limit(self) -> int:
        """
        Get limit (items per page)
        
        Returns:
            int: Number of items per page
        """
        return self.size
    
    def get_sort_dict(self) -> Dict[str, Any]:
        """
        Convert sort parameters to a dictionary format
        
        Returns:
            Dict[str, Any]: Sorting dictionary
        """
        if not self.sort:
            return {}
        
        result = {}
        for sort_param in self.sort:
            # Convert to 1 for ascending, -1 for descending
            direction = 1 if sort_param.direction == SortDirection.ASC else -1
            result[sort_param.field] = direction
        
        return result


T = TypeVar('T')

class Pagination(Generic[T]):
    """
    Pagination utility class for processing database queries
    
    Usage:
        pagination = Pagination[UserModel](
            page_params=PageParams(page=2, size=10),
            query=db.query(UserModel)
        )
        paginated_users = pagination.paginate()
    """
    
    def __init__(self, page_params: PageParams, query: Any):
        """
        Initialize pagination
        
        Args:
            page_params: Page parameters
            query: Database query (SQLAlchemy query or similar)
        """
        self.page_params = page_params
        self.query = query
        self.total: Optional[int] = None
    
    def paginate(self) -> Dict[str, Any]:
        """
        Execute pagination
        
        Returns:
            Dict with pagination information
        """
        # Get total count
        self.total = self.get_total_count()
        
        # Apply pagination
        items = self.get_items()
        
        # Calculate total pages
        total_pages = (self.total + self.page_params.size - 1) // self.page_params.size if self.page_params.size else 0
        
        return {
            "items": items,
            "total": self.total,
            "page": self.page_params.page,
            "size": self.page_params.size,
            "pages": total_pages
        }
    
    def get_total_count(self) -> int:
        """
        Get total count of records
        
        Returns:
            int: Total count
        """
        # This should be overridden for specific database implementations
        # Default implementation for SQLAlchemy
        try:
            return self.query.count()
        except (AttributeError, NotImplementedError):
            # Fallback for query objects without count method
            return len(self.query.all())
    
    def get_items(self) -> List[T]:
        """
        Get items for current page
        
        Returns:
            List[T]: Items for current page
        """
        # This should be overridden for specific database implementations
        # Default implementation for SQLAlchemy
        skip = self.page_params.get_skip()
        limit = self.page_params.get_limit()
        
        try:
            return self.query.offset(skip).limit(limit).all()
        except (AttributeError, NotImplementedError):
            # Fallback for query objects without offset/limit methods
            all_items = self.query.all()
            return all_items[skip:skip + limit]