"""
Core interfaces for dependency injection and service layer abstraction.
This module defines the contracts that services and repositories must implement.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Type variables for generic interfaces
T = TypeVar('T')  # Model type
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)  # Create schema type
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)  # Update schema type
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)  # Response schema type

class RepositoryInterface(Generic[T], ABC):
    """
    Base repository interface for data access operations.
    Implements the Repository pattern for database operations.
    """
    
    @abstractmethod
    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """Get entity by primary key."""
        pass
    
    @abstractmethod
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get all entities with optional filtering and pagination."""
        pass
    
    @abstractmethod
    def create(self, db: Session, obj_in: CreateSchema) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def update(self, db: Session, id: int, obj_in: UpdateSchema) -> Optional[T]:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, db: Session, id: int) -> bool:
        """Delete an entity (soft or hard delete)."""
        pass
    
    @abstractmethod
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        pass

class ServiceInterface(Generic[T, CreateSchema, UpdateSchema, ResponseSchema], ABC):
    """
    Base service interface for business logic operations.
    Implements the Service pattern for business logic abstraction.
    """
    
    @abstractmethod
    def get_by_id(self, db: Session, id: int) -> Optional[ResponseSchema]:
        """Get entity by ID with business logic validation."""
        pass
    
    @abstractmethod
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ResponseSchema]:
        """Get all entities with business logic processing."""
        pass
    
    @abstractmethod
    def create(self, db: Session, obj_in: CreateSchema) -> ResponseSchema:
        """Create entity with business logic validation."""
        pass
    
    @abstractmethod
    def update(self, db: Session, id: int, obj_in: UpdateSchema) -> Optional[ResponseSchema]:
        """Update entity with business logic validation."""
        pass
    
    @abstractmethod
    def delete(self, db: Session, id: int) -> bool:
        """Delete entity with business logic validation."""
        pass
    
    @abstractmethod
    def validate_business_rules(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate business rules for the operation."""
        pass

class UnitOfWorkInterface(ABC):
    """
    Unit of Work interface for transaction management.
    Implements the Unit of Work pattern for transaction handling.
    """
    
    @abstractmethod
    def __enter__(self):
        """Enter the unit of work context."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the unit of work context with proper cleanup."""
        pass
    
    @abstractmethod
    def commit(self):
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    def rollback(self):
        """Rollback the current transaction."""
        pass

class DependencyProviderInterface(ABC):
    """
    Dependency provider interface for dependency injection container.
    Implements the Dependency Injection pattern for service resolution.
    """
    
    @abstractmethod
    def get_service(self, service_type: type) -> Any:
        """Get a service instance by type."""
        pass
    
    @abstractmethod
    def get_repository(self, repository_type: type) -> Any:
        """Get a repository instance by type."""
        pass
    
    @abstractmethod
    def register_service(self, service_type: type, implementation: type):
        """Register a service implementation."""
        pass
    
    @abstractmethod
    def register_repository(self, repository_type: type, implementation: type):
        """Register a repository implementation."""
        pass

# Specific interfaces for common operations
class CRUDServiceInterface(ServiceInterface[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    CRUD service interface with common CRUD operations.
    """
    
    @abstractmethod
    def exists(self, db: Session, id: int) -> bool:
        """Check if entity exists."""
        pass
    
    @abstractmethod
    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ResponseSchema]:
        """Get entity by a specific field value."""
        pass
    
    @abstractmethod
    def get_many_by_field(self, db: Session, field: str, value: Any) -> List[ResponseSchema]:
        """Get multiple entities by a specific field value."""
        pass

class SearchableRepositoryInterface(RepositoryInterface[T]):
    """
    Repository interface with search capabilities.
    """
    
    @abstractmethod
    def search(
        self, 
        db: Session, 
        query: str, 
        fields: List[str],
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Search entities by text query across specified fields."""
        pass
    
    @abstractmethod
    def get_by_filters(
        self, 
        db: Session, 
        filters: Dict[str, Any],
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Get entities by multiple filters."""
        pass

# Export commonly used interfaces
__all__ = [
    "RepositoryInterface",
    "ServiceInterface", 
    "UnitOfWorkInterface",
    "DependencyProviderInterface",
    "CRUDServiceInterface",
    "SearchableRepositoryInterface"
] 