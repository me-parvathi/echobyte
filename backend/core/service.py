"""
Base service implementation with business logic abstraction.
This module provides concrete implementations of service interfaces.
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict, Type
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import HTTPException
from .interfaces import ServiceInterface, CRUDServiceInterface
from .repository import BaseRepository

# Type variables
T = TypeVar('T')  # Model type
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)

class BaseService(ServiceInterface[T, CreateSchema, UpdateSchema, ResponseSchema], Generic[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Base service implementation with business logic abstraction.
    Implements the Service pattern for business logic operations.
    """
    
    def __init__(self, repository: BaseRepository[T, CreateSchema, UpdateSchema], response_model: Type[ResponseSchema]):
        """
        Initialize service with repository and response model.
        
        Args:
            repository: Repository instance for data access
            response_model: Pydantic model for response serialization
        """
        self.repository = repository
        self.response_model = response_model
    
    def get_by_id(self, db: Session, id: int) -> Optional[ResponseSchema]:
        """Get entity by ID with business logic validation."""
        entity = self.repository.get_by_id(db, id)
        if not entity:
            return None
        
        return self.response_model.from_orm(entity)
    
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ResponseSchema]:
        """Get all entities with business logic processing."""
        entities = self.repository.get_all(db, skip, limit, filters)
        return [self.response_model.from_orm(entity) for entity in entities]
    
    def create(self, db: Session, obj_in: CreateSchema) -> ResponseSchema:
        """Create entity with business logic validation."""
        # Validate business rules
        if not self.validate_business_rules(db, obj_in, "create"):
            raise HTTPException(status_code=400, detail="Business rule validation failed")
        
        entity = self.repository.create(db, obj_in)
        return self.response_model.from_orm(entity)
    
    def update(self, db: Session, id: int, obj_in: UpdateSchema) -> Optional[ResponseSchema]:
        """Update entity with business logic validation."""
        # Check if entity exists
        if not self.repository.exists(db, id):
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Validate business rules
        if not self.validate_business_rules(db, obj_in, "update"):
            raise HTTPException(status_code=400, detail="Business rule validation failed")
        
        entity = self.repository.update(db, id, obj_in)
        if not entity:
            return None
        
        return self.response_model.from_orm(entity)
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete entity with business logic validation."""
        # Check if entity exists
        if not self.repository.exists(db, id):
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Validate business rules
        if not self.validate_business_rules(db, {"id": id}, "delete"):
            raise HTTPException(status_code=400, detail="Cannot delete entity due to business rules")
        
        return self.repository.delete(db, id)
    
    def validate_business_rules(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate business rules for the operation."""
        # Base implementation - always return True
        # Override in subclasses to implement specific business rules
        return True
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        return self.repository.count(db, filters)

class CRUDService(BaseService[T, CreateSchema, UpdateSchema, ResponseSchema], CRUDServiceInterface[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    CRUD service with common CRUD operations.
    Extends BaseService with additional CRUD functionality.
    """
    
    def exists(self, db: Session, id: int) -> bool:
        """Check if entity exists."""
        return self.repository.exists(db, id)
    
    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ResponseSchema]:
        """Get entity by a specific field value."""
        entity = self.repository.get_by_field(db, field, value)
        if not entity:
            return None
        
        return self.response_model.from_orm(entity)
    
    def get_many_by_field(self, db: Session, field: str, value: Any) -> List[ResponseSchema]:
        """Get multiple entities by a specific field value."""
        entities = self.repository.get_many_by_field(db, field, value)
        return [self.response_model.from_orm(entity) for entity in entities]
    
    def get_paginated(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get paginated results with metadata."""
        skip = (page - 1) * page_size
        entities = self.repository.get_all(db, skip, page_size, filters)
        total = self.repository.count(db, filters)
        
        return {
            "items": [self.response_model.from_orm(entity) for entity in entities],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

class BusinessRuleService(BaseService[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Service with enhanced business rule validation.
    Extends BaseService with comprehensive business rule checking.
    """
    
    def __init__(self, repository: BaseRepository[T, CreateSchema, UpdateSchema], response_model: Type[ResponseSchema]):
        super().__init__(repository, response_model)
        self.business_rules = []
    
    def add_business_rule(self, rule_func):
        """Add a business rule function."""
        self.business_rules.append(rule_func)
    
    def validate_business_rules(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate all business rules for the operation."""
        for rule in self.business_rules:
            if not rule(db, obj_in, operation):
                return False
        return True
    
    def validate_unique_constraint(self, db: Session, field: str, value: Any, exclude_id: Optional[int] = None) -> bool:
        """Validate unique constraint for a field."""
        existing = self.repository.get_by_field(db, field, value)
        if existing and (exclude_id is None or getattr(existing, 'LocationID') != exclude_id):
            return False
        return True
    
    def validate_foreign_key_constraint(self, db: Session, foreign_key_field: str, foreign_key_value: Any, foreign_model: Type) -> bool:
        """Validate foreign key constraint."""
        foreign_entity = db.query(foreign_model).filter(getattr(foreign_model, 'LocationID') == foreign_key_value).first()
        return foreign_entity is not None
    
    def validate_date_range(self, start_date: Any, end_date: Any) -> bool:
        """Validate date range (start_date <= end_date)."""
        if start_date and end_date:
            return start_date <= end_date
        return True

class AuditService(BaseService[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Service with audit trail functionality.
    Extends BaseService with audit logging.
    """
    
    def __init__(self, repository: BaseRepository[T, CreateSchema, UpdateSchema], response_model: Type[ResponseSchema]):
        super().__init__(repository, response_model)
    
    def create(self, db: Session, obj_in: CreateSchema) -> ResponseSchema:
        """Create entity with audit trail."""
        # Log creation attempt
        self._log_audit_event(db, "CREATE_ATTEMPT", obj_in.dict())
        
        result = super().create(db, obj_in)
        
        # Log successful creation
        self._log_audit_event(db, "CREATE_SUCCESS", {"id": getattr(result, 'LocationID', None)})
        
        return result
    
    def update(self, db: Session, id: int, obj_in: UpdateSchema) -> Optional[ResponseSchema]:
        """Update entity with audit trail."""
        # Log update attempt
        self._log_audit_event(db, "UPDATE_ATTEMPT", {"id": id, "data": obj_in.dict()})
        
        result = super().update(db, id, obj_in)
        
        if result:
            # Log successful update
            self._log_audit_event(db, "UPDATE_SUCCESS", {"id": id})
        else:
            # Log failed update
            self._log_audit_event(db, "UPDATE_FAILED", {"id": id})
        
        return result
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete entity with audit trail."""
        # Log deletion attempt
        self._log_audit_event(db, "DELETE_ATTEMPT", {"id": id})
        
        result = super().delete(db, id)
        
        if result:
            # Log successful deletion
            self._log_audit_event(db, "DELETE_SUCCESS", {"id": id})
        else:
            # Log failed deletion
            self._log_audit_event(db, "DELETE_FAILED", {"id": id})
        
        return result
    
    def _log_audit_event(self, db: Session, event_type: str, data: Dict[str, Any]):
        """Log audit event to database or external system."""
        # This is a placeholder for audit logging
        # In a real implementation, you would log to an audit table or external system
        print(f"AUDIT: {event_type} - {data}")

# Export commonly used service classes
__all__ = [
    "BaseService",
    "CRUDService",
    "BusinessRuleService", 
    "AuditService"
] 