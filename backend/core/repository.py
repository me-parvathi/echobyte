"""
Base repository implementation with common CRUD operations.
This module provides concrete implementations of repository interfaces.
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict, Type
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_
from pydantic import BaseModel
from .interfaces import RepositoryInterface, SearchableRepositoryInterface

# Type variables
T = TypeVar('T')  # Model type
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)

class BaseRepository(RepositoryInterface[T], Generic[T, CreateSchema, UpdateSchema]):
    """
    Base repository implementation with common CRUD operations.
    Implements the Repository pattern for database operations.
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with the model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def _get_primary_key_column(self):
        """Get the primary key column for the model."""
        # Get the primary key columns
        pk_columns = self.model.__table__.primary_key.columns
        if pk_columns:
            # Return the first primary key column
            return list(pk_columns)[0]
        # Fallback to a common primary key name
        fallback = getattr(self.model, 'ID', None) or getattr(self.model, f'{self.model.__name__}ID', None)
        return fallback
    
    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """Get entity by primary key."""
        return db.query(self.model).filter(self.model.LocationID == id).first()
    
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get all entities with optional filtering and pagination."""
        query = db.query(self.model)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        # Get primary key for ordering
        pk_column = self._get_primary_key_column()
        if pk_column is not None:
            query = query.order_by(pk_column)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchema) -> T:
        """Create a new entity."""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: int, obj_in: UpdateSchema) -> Optional[T]:
        """Update an existing entity."""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete an entity (soft delete by default)."""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return False
        
        # Soft delete - set IsActive to False if the field exists
        if hasattr(db_obj, 'IsActive'):
            db_obj.IsActive = False
            db.commit()
        else:
            # Hard delete if no IsActive field
            db.delete(db_obj)
            db.commit()
        
        return True
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        query = db.query(self.model)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        return query.count()
    
    def exists(self, db: Session, id: int) -> bool:
        """Check if entity exists."""
        return db.query(self.model).filter(self.model.LocationID == id).first() is not None
    
    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[T]:
        """Get entity by a specific field value."""
        return db.query(self.model).filter(getattr(self.model, field) == value).first()
    
    def get_many_by_field(self, db: Session, field: str, value: Any) -> List[T]:
        """Get multiple entities by a specific field value."""
        return db.query(self.model).filter(getattr(self.model, field) == value).all()
    
    def _apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """Apply filters to the query."""
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    query = query.filter(getattr(self.model, field).in_(value))
                elif isinstance(value, dict):
                    # Handle range queries like {"min": 10, "max": 20}
                    if "min" in value and "max" in value:
                        query = query.filter(
                            and_(
                                getattr(self.model, field) >= value["min"],
                                getattr(self.model, field) <= value["max"]
                            )
                        )
                    elif "min" in value:
                        query = query.filter(getattr(self.model, field) >= value["min"])
                    elif "max" in value:
                        query = query.filter(getattr(self.model, field) <= value["max"])
                else:
                    query = query.filter(getattr(self.model, field) == value)
        
        return query

class SearchableRepository(BaseRepository[T, CreateSchema, UpdateSchema], SearchableRepositoryInterface[T], Generic[T, CreateSchema, UpdateSchema]):
    """
    Searchable repository with text search capabilities.
    Extends BaseRepository with search functionality.
    """
    
    def search(
        self, 
        db: Session, 
        query: str, 
        fields: List[str],
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Search entities by text query across specified fields."""
        search_conditions = []
        
        for field in fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).ilike(f"%{query}%")
                )
        
        if not search_conditions:
            return []
        
        # Get primary key for ordering
        pk_column = self._get_primary_key_column()
        
        query = db.query(self.model).filter(or_(*search_conditions))
        
        if pk_column is not None:
            query = query.order_by(pk_column)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_filters(
        self, 
        db: Session, 
        filters: Dict[str, Any],
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Get entities by multiple filters."""
        return self.get_all(db, skip, limit, filters)

class SoftDeleteRepository(BaseRepository[T, CreateSchema, UpdateSchema], Generic[T, CreateSchema, UpdateSchema]):
    """
    Repository with soft delete functionality.
    Extends BaseRepository with soft delete behavior.
    """
    
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> List[T]:
        """Get all entities, optionally including deleted ones."""
        query = db.query(self.model)
        
        # Only include active records unless explicitly requested
        if not include_deleted and hasattr(self.model, 'IsActive'):
            query = query.filter(self.model.IsActive == True)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        # Get primary key for ordering
        pk_column = self._get_primary_key_column()
        if pk_column is not None:
            query = query.order_by(pk_column)
        
        return query.offset(skip).limit(limit).all()
    
    def hard_delete(self, db: Session, id: int) -> bool:
        """Hard delete an entity (permanently remove from database)."""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True
    
    def restore(self, db: Session, id: int) -> bool:
        """Restore a soft-deleted entity."""
        if not hasattr(self.model, 'IsActive'):
            return False
        
        db_obj = db.query(self.model).filter(
            and_(
                self.model.LocationID == id,
                self.model.IsActive == False
            )
        ).first()
        
        if not db_obj:
            return False
        
        db_obj.IsActive = True
        db.commit()
        return True

# Export commonly used repository classes
__all__ = [
    "BaseRepository",
    "SearchableRepository", 
    "SoftDeleteRepository"
] 