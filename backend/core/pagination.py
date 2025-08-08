"""
Pagination utilities for consistent API responses
"""

from typing import List, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.orm import Query
from sqlalchemy import desc

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    items: List[T]
    total_count: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

def paginate_query(
    query: Query,
    skip: int = 0,
    limit: int = 100,
    order_by_column=None,
    order_desc: bool = True
) -> dict:
    """
    Paginate a SQLAlchemy query and return standardized response
    
    Args:
        query: SQLAlchemy query to paginate
        skip: Number of items to skip
        limit: Number of items to return
        order_by_column: Column to order by (defaults to first primary key)
        order_desc: Whether to order descending (default True)
    
    Returns:
        dict with paginated results and metadata
    """
    # Get total count before pagination
    total_count = query.count()
    
    # Apply ordering
    if order_by_column:
        if order_desc:
            query = query.order_by(desc(order_by_column))
        else:
            query = query.order_by(order_by_column)
    
    # Get paginated results
    items = query.offset(skip).limit(limit).all()
    
    # Calculate pagination info
    page = (skip // limit) + 1 if limit > 0 else 1
    has_next = (skip + limit) < total_count
    has_previous = skip > 0
    
    return {
        "items": items,
        "total_count": total_count,
        "page": page,
        "size": limit,
        "has_next": has_next,
        "has_previous": has_previous
    }

def create_list_response(
    items: List,
    total_count: int,
    page: int,
    size: int
) -> dict:
    """
    Create a standardized list response
    
    Args:
        items: List of items
        total_count: Total number of items
        page: Current page number
        size: Page size
    
    Returns:
        dict with standardized response format
    """
    has_next = ((page - 1) * size + len(items)) < total_count
    has_previous = page > 1
    
    return {
        "items": items,
        "total_count": total_count,
        "page": page,
        "size": size,
        "has_next": has_next,
        "has_previous": has_previous
    } 