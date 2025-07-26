"""
Location service implementation using the Service pattern.
This module provides business logic operations for Location entities.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.service import BusinessRuleService
from . import models, schemas
from .repository import LocationRepository

class LocationService(BusinessRuleService[models.Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.Location]):
    """
    Location service implementation.
    Extends BusinessRuleService with Location-specific business logic.
    """
    
    def __init__(self):
        """Initialize location service with repository and response model."""
        repository = LocationRepository()
        super().__init__(repository, schemas.Location)
        
        # Add business rules
        self.add_business_rule(self._validate_location_name_unique)
        self.add_business_rule(self._validate_location_data)
        self.add_business_rule(self._validate_location_deletion)
    
    def get_by_id(self, db: Session, id: int) -> Optional[schemas.Location]:
        """Get location by ID with business logic validation."""
        location = self.repository.get_by_id(db, id)
        if not location:
            return None
        
        return schemas.Location.from_orm(location)
    
    def get_by_name(self, db: Session, name: str) -> Optional[schemas.Location]:
        """Get location by name."""
        location = self.repository.get_by_name(db, name)
        if not location:
            return None
        
        return schemas.Location.from_orm(location)
    
    def get_active_locations(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get all active locations."""
        locations = self.repository.get_active_locations(db, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_by_country(self, db: Session, country: str, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations by country."""
        locations = self.repository.get_locations_by_country(db, country, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_by_city(self, db: Session, city: str, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations by city."""
        locations = self.repository.get_locations_by_city(db, city, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def search_locations(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Search locations by name, city, or country."""
        locations = self.repository.search_locations(db, query, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_with_departments(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations that have departments."""
        locations = self.repository.get_locations_with_departments(db, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def count_locations_by_country(self, db: Session) -> Dict[str, int]:
        """Count locations grouped by country."""
        return self.repository.count_locations_by_country(db)
    
    def get_locations_by_timezone(self, db: Session, timezone: str, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations by timezone."""
        locations = self.repository.get_locations_by_timezone(db, timezone, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_by_state(self, db: Session, state: str, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations by state."""
        locations = self.repository.get_locations_by_state(db, state, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_with_phone(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations that have phone numbers."""
        locations = self.repository.get_locations_with_phone(db, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def get_locations_with_postal_code(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Location]:
        """Get locations that have postal codes."""
        locations = self.repository.get_locations_with_postal_code(db, skip, limit)
        return [schemas.Location.from_orm(location) for location in locations]
    
    def create_location(self, db: Session, location: schemas.LocationCreate) -> schemas.Location:
        """Create a new location with business logic validation."""
        return self.create(db, location)
    
    def update_location(self, db: Session, location_id: int, location_update: schemas.LocationUpdate) -> Optional[schemas.Location]:
        """Update an existing location with business logic validation."""
        return self.update(db, location_id, location_update)
    
    def delete_location(self, db: Session, location_id: int) -> bool:
        """Delete a location with business logic validation."""
        return self.delete(db, location_id)
    
    def restore_location(self, db: Session, location_id: int) -> bool:
        """Restore a soft-deleted location."""
        if not hasattr(self.repository, 'restore'):
            raise HTTPException(status_code=400, detail="Restore operation not supported")
        
        return self.repository.restore(db, location_id)
    
    # Business rule validation methods
    def _validate_location_name_unique(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate that location name is unique."""
        if operation == "create":
            if not self.repository.validate_location_name_unique(db, obj_in.LocationName):
                raise HTTPException(status_code=400, detail="Location name already exists")
        elif operation == "update":
            # For updates, we need to exclude the current location ID
            location_id = getattr(obj_in, 'LocationID', None)
            if not self.repository.validate_location_name_unique(db, obj_in.LocationName, location_id):
                raise HTTPException(status_code=400, detail="Location name already exists")
        
        return True
    
    def _validate_location_data(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate location data integrity."""
        if operation in ["create", "update"]:
            # Validate required fields
            if not obj_in.LocationName or not obj_in.LocationName.strip():
                raise HTTPException(status_code=400, detail="Location name is required")
            
            if not obj_in.Address1 or not obj_in.Address1.strip():
                raise HTTPException(status_code=400, detail="Address1 is required")
            
            if not obj_in.City or not obj_in.City.strip():
                raise HTTPException(status_code=400, detail="City is required")
            
            if not obj_in.Country or not obj_in.Country.strip():
                raise HTTPException(status_code=400, detail="Country is required")
            
            if not obj_in.TimeZone or not obj_in.TimeZone.strip():
                raise HTTPException(status_code=400, detail="TimeZone is required")
            
            # Validate phone number format (basic validation)
            if obj_in.Phone and not self._is_valid_phone(obj_in.Phone):
                raise HTTPException(status_code=400, detail="Invalid phone number format")
            
            # Validate postal code format (basic validation)
            if obj_in.PostalCode and not self._is_valid_postal_code(obj_in.PostalCode):
                raise HTTPException(status_code=400, detail="Invalid postal code format")
        
        return True
    
    def _validate_location_deletion(self, db: Session, obj_in: Any, operation: str) -> bool:
        """Validate location deletion rules."""
        if operation == "delete":
            location_id = obj_in.get("id")
            if location_id:
                # Check if location has departments
                from api.department.models import Department
                departments_count = db.query(Department).filter(Department.LocationID == location_id).count()
                
                if departments_count > 0:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot delete location with {departments_count} departments"
                    )
        
        return True
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        import re
        # Basic phone validation - allows digits, spaces, dashes, parentheses, and plus sign
        phone_pattern = r'^[\+]?[0-9\s\-\(\)]+$'
        return bool(re.match(phone_pattern, phone.strip()))
    
    def _is_valid_postal_code(self, postal_code: str) -> bool:
        """Validate postal code format."""
        import re
        # Basic postal code validation - allows alphanumeric characters
        postal_pattern = r'^[A-Za-z0-9\s\-]+$'
        return bool(re.match(postal_pattern, postal_code.strip()))
    
    def get_location_statistics(self, db: Session) -> Dict[str, Any]:
        """Get location statistics for reporting."""
        total_locations = self.repository.count(db)
        active_locations = self.repository.count(db, {"IsActive": True})
        inactive_locations = total_locations - active_locations
        
        countries = self.repository.count_locations_by_country(db)
        total_countries = len(countries)
        
        # Get locations with phone numbers
        locations_with_phone = len(self.repository.get_locations_with_phone(db, limit=1000))
        
        # Get locations with postal codes
        locations_with_postal = len(self.repository.get_locations_with_postal_code(db, limit=1000))
        
        return {
            "total_locations": total_locations,
            "active_locations": active_locations,
            "inactive_locations": inactive_locations,
            "total_countries": total_countries,
            "locations_with_phone": locations_with_phone,
            "locations_with_postal_code": locations_with_postal,
            "countries_breakdown": countries
        } 