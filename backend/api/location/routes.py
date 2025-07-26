"""
Location routes using service pattern.
This module provides FastAPI endpoints for Location management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.database import get_db
from . import schemas, service

# Create router
router = APIRouter()

@router.get("/", response_model=List[schemas.Location])
def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    timezone: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of locations with optional filtering"""
    location_service = service.LocationService()
    
    # Use search if provided
    if search:
        return location_service.search_locations(db, search, skip, limit)
    
    # Create filters dict
    filters = {}
    if is_active is not None:
        filters["IsActive"] = is_active
    if country:
        filters["Country"] = country
    if city:
        filters["City"] = city
    if state:
        filters["State"] = state
    if timezone:
        filters["TimeZone"] = timezone
    
    locations = location_service.get_all(db, skip=skip, limit=limit, filters=filters)
    return locations

@router.get("/active", response_model=List[schemas.Location])
def get_active_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all active locations"""
    location_service = service.LocationService()
    return location_service.get_active_locations(db, skip, limit)

@router.get("/country/{country}", response_model=List[schemas.Location])
def get_locations_by_country(
    country: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations by country"""
    location_service = service.LocationService()
    return location_service.get_locations_by_country(db, country, skip, limit)

@router.get("/city/{city}", response_model=List[schemas.Location])
def get_locations_by_city(
    city: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations by city"""
    location_service = service.LocationService()
    return location_service.get_locations_by_city(db, city, skip, limit)

@router.get("/state/{state}", response_model=List[schemas.Location])
def get_locations_by_state(
    state: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations by state"""
    location_service = service.LocationService()
    return location_service.get_locations_by_state(db, state, skip, limit)

@router.get("/timezone/{timezone:path}", response_model=List[schemas.Location])
def get_locations_by_timezone(
    timezone: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations by timezone"""
    # Handle URL encoding issues - try both with space and underscore
    # Database stores "America/Los_Angeles" but URL might be "America/Los Angeles"
    location_service = service.LocationService()
    
    print(f"DEBUG: Original timezone parameter: '{timezone}'")
    
    # First try with the original timezone
    locations = location_service.get_locations_by_timezone(db, timezone, skip, limit)
    print(f"DEBUG: Results with original timezone: {len(locations)}")
    
    # If no results, try with underscore replaced by space
    if not locations:
        normalized_timezone = timezone.replace("_", " ")
        print(f"DEBUG: Trying with underscore->space: '{normalized_timezone}'")
        locations = location_service.get_locations_by_timezone(db, normalized_timezone, skip, limit)
        print(f"DEBUG: Results with underscore->space: {len(locations)}")
    
    # If still no results, try with space replaced by underscore
    if not locations:
        normalized_timezone = timezone.replace(" ", "_")
        print(f"DEBUG: Trying with space->underscore: '{normalized_timezone}'")
        locations = location_service.get_locations_by_timezone(db, normalized_timezone, skip, limit)
        print(f"DEBUG: Results with space->underscore: {len(locations)}")
    
    print(f"DEBUG: Final result count: {len(locations)}")
    return locations

@router.get("/with-departments", response_model=List[schemas.Location])
def get_locations_with_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations that have departments"""
    location_service = service.LocationService()
    return location_service.get_locations_with_departments(db, skip, limit)

@router.get("/with-phone", response_model=List[schemas.Location])
def get_locations_with_phone(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations that have phone numbers"""
    location_service = service.LocationService()
    return location_service.get_locations_with_phone(db, skip, limit)

@router.get("/with-postal-code", response_model=List[schemas.Location])
def get_locations_with_postal_code(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get locations that have postal codes"""
    location_service = service.LocationService()
    return location_service.get_locations_with_postal_code(db, skip, limit)

@router.get("/statistics")
def get_location_statistics(db: Session = Depends(get_db)):
    """Get location statistics for reporting"""
    location_service = service.LocationService()
    return location_service.get_location_statistics(db)

@router.get("/name/{location_name}", response_model=schemas.Location)
def get_location_by_name(location_name: str, db: Session = Depends(get_db)):
    """Get a specific location by name"""
    location_service = service.LocationService()
    location = location_service.get_by_name(db, location_name)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.get("/{location_id}", response_model=schemas.Location)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location_service = service.LocationService()
    location = location_service.get_by_id(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/", response_model=schemas.Location, status_code=201)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    location_service = service.LocationService()
    return location_service.create(db, location)

@router.put("/{location_id}", response_model=schemas.Location)
def update_location(
    location_id: int, 
    location_update: schemas.LocationUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing location"""
    location_service = service.LocationService()
    location = location_service.update(db, location_id, location_update)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Soft delete a location (set IsActive to False)"""
    location_service = service.LocationService()
    success = location_service.delete(db, location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    return None

@router.post("/{location_id}/restore", response_model=schemas.Location)
def restore_location(location_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted location"""
    location_service = service.LocationService()
    success = location_service.restore_location(db, location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found or cannot be restored")
    
    # Return the restored location
    return location_service.get_by_id(db, location_id) 