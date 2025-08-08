from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException

class DepartmentService:
    
    @staticmethod
    def get_department(db: Session, department_id: int) -> Optional[models.Department]:
        return db.query(models.Department).filter(models.Department.DepartmentID == department_id).first()
    
    @staticmethod
    def get_department_by_code(db: Session, department_code: str) -> Optional[models.Department]:
        return db.query(models.Department).filter(models.Department.DepartmentCode == department_code).first()
    
    @staticmethod
    def get_departments(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        location_id: Optional[int] = None,
        parent_id: Optional[int] = None
    ) -> List[models.Department]:
        query = db.query(models.Department)
        
        if is_active is not None:
            query = query.filter(models.Department.IsActive == is_active)
        
        if location_id:
            query = query.filter(models.Department.LocationID == location_id)
        
        if parent_id is not None:
            if parent_id == 0:  # Root departments
                query = query.filter(models.Department.ParentDepartmentID.is_(None))
            else:
                query = query.filter(models.Department.ParentDepartmentID == parent_id)
        
        return query.order_by(models.Department.DepartmentID).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_department(db: Session, department: schemas.DepartmentCreate) -> models.Department:
        # Check if department code already exists
        if DepartmentService.get_department_by_code(db, department.DepartmentCode):
            raise HTTPException(status_code=400, detail="Department code already exists")
        
        # Validate parent department exists
        if department.ParentDepartmentID:
            parent = DepartmentService.get_department(db, department.ParentDepartmentID)
            if not parent:
                raise HTTPException(status_code=400, detail="Parent department not found")
        
        db_department = models.Department(**department.dict())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department
    
    @staticmethod
    def update_department(db: Session, department_id: int, department_update: schemas.DepartmentUpdate) -> Optional[models.Department]:
        db_department = DepartmentService.get_department(db, department_id)
        if not db_department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        update_data = department_update.dict(exclude_unset=True)
        
        # Check for unique constraints
        if 'DepartmentCode' in update_data:
            existing = DepartmentService.get_department_by_code(db, update_data['DepartmentCode'])
            if existing and existing.DepartmentID != department_id:
                raise HTTPException(status_code=400, detail="Department code already exists")
        
        # Validate parent department exists
        if 'ParentDepartmentID' in update_data and update_data['ParentDepartmentID']:
            parent = DepartmentService.get_department(db, update_data['ParentDepartmentID'])
            if not parent:
                raise HTTPException(status_code=400, detail="Parent department not found")
        
        for field, value in update_data.items():
            setattr(db_department, field, value)
        
        db.commit()
        db.refresh(db_department)
        return db_department
    
    @staticmethod
    def delete_department(db: Session, department_id: int) -> bool:
        db_department = DepartmentService.get_department(db, department_id)
        if not db_department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Check if department has child departments
        child_departments = db.query(models.Department).filter(
            models.Department.ParentDepartmentID == department_id
        ).count()
        
        if child_departments > 0:
            raise HTTPException(status_code=400, detail="Cannot delete department with child departments")
        
        # Soft delete - set IsActive to False
        db_department.IsActive = False
        db.commit()
        return True
    
    @staticmethod
    def get_department_hierarchy(db: Session, department_id: int) -> List[models.Department]:
        """Get department hierarchy (parent chain)"""
        hierarchy = []
        current_department = DepartmentService.get_department(db, department_id)
        
        while current_department and current_department.ParentDepartmentID:
            parent = DepartmentService.get_department(db, current_department.ParentDepartmentID)
            if parent:
                hierarchy.append(parent)
                current_department = parent
            else:
                break
        
        return hierarchy

class LocationService:
    
    @staticmethod
    def get_location(db: Session, location_id: int) -> Optional[models.Location]:
        return db.query(models.Location).filter(models.Location.LocationID == location_id).first()
    
    @staticmethod
    def get_location_by_name(db: Session, location_name: str) -> Optional[models.Location]:
        return db.query(models.Location).filter(models.Location.LocationName == location_name).first()
    
    @staticmethod
    def get_locations(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        country: Optional[str] = None
    ) -> List[models.Location]:
        query = db.query(models.Location)
        
        if is_active is not None:
            query = query.filter(models.Location.IsActive == is_active)
        
        if country:
            query = query.filter(models.Location.Country == country)
        
        return query.order_by(models.Location.LocationID).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_location(db: Session, location: schemas.LocationCreate) -> models.Location:
        # Check if location name already exists
        if LocationService.get_location_by_name(db, location.LocationName):
            raise HTTPException(status_code=400, detail="Location name already exists")
        
        db_location = models.Location(**location.dict())
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location
    
    @staticmethod
    def update_location(db: Session, location_id: int, location_update: schemas.LocationUpdate) -> Optional[models.Location]:
        db_location = LocationService.get_location(db, location_id)
        if not db_location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        update_data = location_update.dict(exclude_unset=True)
        
        # Check for unique constraints
        if 'LocationName' in update_data:
            existing = LocationService.get_location_by_name(db, update_data['LocationName'])
            if existing and existing.LocationID != location_id:
                raise HTTPException(status_code=400, detail="Location name already exists")
        
        for field, value in update_data.items():
            setattr(db_location, field, value)
        
        db.commit()
        db.refresh(db_location)
        return db_location
    
    @staticmethod
    def delete_location(db: Session, location_id: int) -> bool:
        db_location = LocationService.get_location(db, location_id)
        if not db_location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Check if location has departments
        departments_count = db.query(models.Department).filter(
            models.Department.LocationID == location_id
        ).count()
        
        if departments_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete location with departments")
        
        # Soft delete - set IsActive to False
        db_location.IsActive = False
        db.commit()
        return True 