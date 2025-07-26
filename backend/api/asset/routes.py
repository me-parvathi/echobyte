from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Asset routes
@router.get("/", response_model=List[schemas.AssetResponse])
def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    asset_type_id: Optional[int] = None,
    status_code: Optional[str] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of assets with optional filtering"""
    return service.AssetService.get_assets(db, skip, limit, asset_type_id, status_code, location_id)

@router.get("/{asset_id}", response_model=schemas.AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get a specific asset by ID"""
    asset = service.AssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=schemas.AssetResponse, status_code=201)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    """Create a new asset"""
    return service.AssetService.create_asset(db, asset)

@router.put("/{asset_id}", response_model=schemas.AssetResponse)
def update_asset(
    asset_id: int, 
    asset_update: schemas.AssetUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing asset"""
    return service.AssetService.update_asset(db, asset_id, asset_update)

@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete an asset"""
    service.AssetService.delete_asset(db, asset_id)
    return None

# Asset Type routes
@router.get("/types", response_model=List[schemas.AssetTypeResponse])
def get_asset_types(db: Session = Depends(get_db)):
    """Get list of asset types"""
    return service.AssetService.get_asset_types(db)

@router.get("/types/{type_id}", response_model=schemas.AssetTypeResponse)
def get_asset_type(type_id: int, db: Session = Depends(get_db)):
    """Get a specific asset type by ID"""
    asset_type = service.AssetService.get_asset_type(db, type_id)
    if not asset_type:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return asset_type

@router.post("/types", response_model=schemas.AssetTypeResponse, status_code=201)
def create_asset_type(asset_type: schemas.AssetTypeCreate, db: Session = Depends(get_db)):
    """Create a new asset type"""
    return service.AssetService.create_asset_type(db, asset_type)

@router.put("/types/{type_id}", response_model=schemas.AssetTypeResponse)
def update_asset_type(
    type_id: int, 
    asset_type_update: schemas.AssetTypeUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing asset type"""
    return service.AssetService.update_asset_type(db, type_id, asset_type_update)

@router.delete("/types/{type_id}", status_code=204)
def delete_asset_type(type_id: int, db: Session = Depends(get_db)):
    """Delete an asset type"""
    service.AssetService.delete_asset_type(db, type_id)
    return None

# Asset Assignment routes
@router.get("/assignments", response_model=List[schemas.AssetAssignmentResponse])
def get_asset_assignments(
    asset_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get asset assignments with optional filtering"""
    return service.AssetService.get_asset_assignments(db, asset_id, employee_id, is_active)

@router.get("/assignments/{assignment_id}", response_model=schemas.AssetAssignmentResponse)
def get_asset_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get a specific asset assignment by ID"""
    assignment = service.AssetService.get_asset_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Asset assignment not found")
    return assignment

@router.post("/assignments", response_model=schemas.AssetAssignmentResponse, status_code=201)
def create_asset_assignment(assignment: schemas.AssetAssignmentCreate, db: Session = Depends(get_db)):
    """Create a new asset assignment"""
    return service.AssetService.create_asset_assignment(db, assignment)

@router.put("/assignments/{assignment_id}", response_model=schemas.AssetAssignmentResponse)
def update_asset_assignment(
    assignment_id: int, 
    assignment_update: schemas.AssetAssignmentUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing asset assignment"""
    return service.AssetService.update_asset_assignment(db, assignment_id, assignment_update)

@router.delete("/assignments/{assignment_id}", status_code=204)
def delete_asset_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Delete an asset assignment"""
    service.AssetService.delete_asset_assignment(db, assignment_id)
    return None

# Asset Status routes
@router.get("/statuses", response_model=List[schemas.AssetStatusResponse])
def get_asset_statuses(db: Session = Depends(get_db)):
    """Get list of asset statuses"""
    return service.AssetService.get_asset_statuses(db) 