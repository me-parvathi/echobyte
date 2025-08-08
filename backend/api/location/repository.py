"""
Location repository implementation using the Repository pattern.
This module provides data access operations for Location entities.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from core.repository import SearchableRepository
from . import models, schemas

class LocationRepository(SearchableRepository[models.Location, schemas.LocationCreate, schemas.LocationUpdate]):
    """
    Location repository implementation.
    Extends SearchableRepository with Location-specific operations.
    """
    
    def __init__(self):
        super().__init__(models.Location)
    
    def get_by_id(self, db: Session, id: int) -> Optional[models.Location]:
        """Get location by ID."""
        return db.query(models.Location).filter(models.Location.LocationID == id).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[models.Location]:
        """Get location by name."""
        return db.query(models.Location).filter(models.Location.LocationName == name).first()
    
    def get_active_locations(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get all active locations."""
        return (
            db.query(models.Location)
            .filter(models.Location.IsActive == True)
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_locations_by_country(self, db: Session, country: str, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations by country."""
        return (
            db.query(models.Location)
            .filter(models.Location.Country == country)
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_locations_by_city(self, db: Session, city: str, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations by city."""
        return (
            db.query(models.Location)
            .filter(models.Location.City == city)
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_locations(
        self, 
        db: Session, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Location]:
        """Search locations by name, city, or country."""
        search_fields = ["LocationName", "City", "Country"]
        return self.search(db, query, search_fields, skip, limit)
    
    def get_locations_with_departments(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations that have departments."""
        from api.department.models import Department
        
        return (
            db.query(models.Location)
            .join(Department, models.Location.LocationID == Department.LocationID)
            .distinct()
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_locations_by_country(self, db: Session) -> Dict[str, int]:
        """Count locations grouped by country."""
        result = (
            db.query(models.Location.Country, db.func.count(models.Location.LocationID))
            .group_by(models.Location.Country)
            .all()
        )
        return dict(result)
    
    def get_locations_by_timezone(self, db: Session, timezone: str, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations by timezone."""
        print(f"DEBUG: Repository searching for timezone: '{timezone}'")
        
        # First, let's see what timezones exist in the database
        all_timezones = db.query(models.Location.TimeZone).distinct().all()
        print(f"DEBUG: Available timezones in DB: {[tz[0] for tz in all_timezones]}")
        
        result = (
            db.query(models.Location)
            .filter(models.Location.TimeZone == timezone)
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        print(f"DEBUG: Found {len(result)} locations for timezone '{timezone}'")
        return result
    
    def validate_location_name_unique(self, db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        """Validate that location name is unique."""
        query = db.query(models.Location).filter(models.Location.LocationName == name)
        
        if exclude_id:
            query = query.filter(models.Location.LocationID != exclude_id)
        
        return query.first() is None
    
    def get_locations_with_phone(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations that have phone numbers."""
        return (
            db.query(models.Location)
            .filter(models.Location.Phone.isnot(None))
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_locations_by_state(self, db: Session, state: str, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations by state."""
        return (
            db.query(models.Location)
            .filter(models.Location.State == state)
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_locations_with_postal_code(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
        """Get locations that have postal codes."""
        return (
            db.query(models.Location)
            .filter(models.Location.PostalCode.isnot(None))
            .order_by(models.Location.LocationID)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def restore(self, db: Session, id: int) -> bool:
        """Restore a soft-deleted location."""
        if not hasattr(models.Location, 'IsActive'):
            return False
        
        db_obj = db.query(models.Location).filter(
            and_(
                models.Location.LocationID == id,
                models.Location.IsActive == False
            )
        ).first()
        
        if not db_obj:
            return False
        
        db_obj.IsActive = True
        db.commit()
        return True 