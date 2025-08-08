from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Department routes
@router.get("/", response_model=schemas.DepartmentListResponse)
def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    location_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of departments with optional filtering"""
    departments = service.DepartmentService.get_departments(
        db, skip=skip, limit=limit, 
        is_active=is_active, location_id=location_id, parent_id=parent_id
    )
    total = len(departments)
    return schemas.DepartmentListResponse(
        departments=departments, total=total, page=skip//limit + 1, size=limit
    )

@router.get("/{department_id}", response_model=schemas.DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    """Get a specific department by ID"""
    department = service.DepartmentService.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.post("/", response_model=schemas.DepartmentResponse, status_code=201)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    """Create a new department"""
    return service.DepartmentService.create_department(db, department)

@router.put("/{department_id}", response_model=schemas.DepartmentResponse)
def update_department(
    department_id: int, 
    department_update: schemas.DepartmentUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing department"""
    return service.DepartmentService.update_department(db, department_id, department_update)

@router.delete("/{department_id}", status_code=204)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    """Soft delete a department (set IsActive to False)"""
    service.DepartmentService.delete_department(db, department_id)
    return None

@router.get("/{department_id}/hierarchy", response_model=List[schemas.DepartmentResponse])
def get_department_hierarchy(department_id: int, db: Session = Depends(get_db)):
    """Get department hierarchy (parent chain)"""
    hierarchy = service.DepartmentService.get_department_hierarchy(db, department_id)
    return hierarchy

# Location routes
@router.get("/locations/", response_model=schemas.LocationListResponse)
def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of locations with optional filtering"""
    locations = service.LocationService.get_locations(
        db, skip=skip, limit=limit, is_active=is_active, country=country
    )
    total = len(locations)
    return schemas.LocationListResponse(
        locations=locations, total=total, page=skip//limit + 1, size=limit
    )

@router.get("/locations/{location_id}", response_model=schemas.LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = service.LocationService.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/locations/", response_model=schemas.LocationResponse, status_code=201)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    return service.LocationService.create_location(db, location)

@router.put("/locations/{location_id}", response_model=schemas.LocationResponse)
def update_location(
    location_id: int, 
    location_update: schemas.LocationUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing location"""
    return service.LocationService.update_location(db, location_id, location_update)

@router.delete("/locations/{location_id}", status_code=204)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Soft delete a location (set IsActive to False)"""
    service.LocationService.delete_location(db, location_id)
    return None 