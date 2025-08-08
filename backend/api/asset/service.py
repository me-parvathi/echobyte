from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from . import models, schemas
from fastapi import HTTPException
from core.pagination import paginate_query

class AssetService:
    @staticmethod
    def get_assets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        asset_type_id: Optional[int] = None,
        status_code: Optional[str] = None,
        location_id: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get list of assets with optional filtering and sorting"""
        query = db.query(models.Asset)
        
        # Filtering
        if asset_type_id:
            query = query.filter(models.Asset.AssetTypeID == asset_type_id)
        if status_code:
            query = query.filter(models.Asset.AssetStatusCode == status_code)
        if location_id:
            query = query.filter(models.Asset.LocationID == location_id)
        
        # Sorting
        sort_column_map = {
            "created_at": models.Asset.CreatedAt,
            "updated_at": models.Asset.UpdatedAt,
            "asset_tag": models.Asset.AssetTag,
            "purchase_date": models.Asset.PurchaseDate,
            "warranty_end_date": models.Asset.WarrantyEndDate,
            "contract_expiry_date": models.Asset.ContractExpiryDate,
        }
        
        print(f"DEBUG: sort_by={sort_by}, sort_order={sort_order}")
        print(f"DEBUG: Available sort fields: {list(sort_column_map.keys())}")
        
        # Determine order column and direction
        order_column = models.Asset.AssetID  # Default
        order_desc = False
        
        if sort_by and sort_by in sort_column_map:
            order_column = sort_column_map[sort_by]
            order_desc = sort_order == "desc"
            print(f"DEBUG: Using column {order_column} for sorting")
        else:
            print(f"DEBUG: Using default sorting by AssetID")

        # Use pagination utility
        result = paginate_query(
            query=query,
            skip=skip,
            limit=limit,
            order_by_column=order_column,
            order_desc=order_desc
        )
        
        # Debug: Check if warranty dates are present
        for asset in result["items"]:
            print(f"DEBUG: Asset {asset.AssetTag} - WarrantyEndDate: {asset.WarrantyEndDate}")
        
        return result

    @staticmethod
    def get_asset(db: Session, asset_id: int) -> Optional[models.Asset]:
        """Get a specific asset by ID"""
        return db.query(models.Asset).filter(models.Asset.AssetID == asset_id).first()

    @staticmethod
    def create_asset(db: Session, asset: schemas.AssetCreate) -> models.Asset:
        """Create a new asset"""
        db_asset = models.Asset(**asset.dict())
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset

    @staticmethod
    def update_asset(db: Session, asset_id: int, asset_update: schemas.AssetUpdate) -> models.Asset:
        """Update an existing asset"""
        db_asset = db.query(models.Asset).filter(models.Asset.AssetID == asset_id).first()
        if not db_asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        update_data = asset_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_asset, field, value)
        
        db.commit()
        db.refresh(db_asset)
        return db_asset

    @staticmethod
    def delete_asset(db: Session, asset_id: int) -> None:
        """Delete an asset"""
        db_asset = db.query(models.Asset).filter(models.Asset.AssetID == asset_id).first()
        if not db_asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        db.delete(db_asset)
        db.commit()

    # Asset Type methods
    @staticmethod
    def get_asset_types(db: Session) -> List[models.AssetType]:
        """Get list of asset types"""
        return db.query(models.AssetType).all()

    @staticmethod
    def get_asset_type(db: Session, type_id: int) -> Optional[models.AssetType]:
        """Get a specific asset type by ID"""
        return db.query(models.AssetType).filter(models.AssetType.AssetTypeID == type_id).first()

    @staticmethod
    def create_asset_type(db: Session, asset_type: schemas.AssetTypeCreate) -> models.AssetType:
        """Create a new asset type"""
        db_asset_type = models.AssetType(**asset_type.dict())
        db.add(db_asset_type)
        db.commit()
        db.refresh(db_asset_type)
        return db_asset_type

    @staticmethod
    def update_asset_type(db: Session, type_id: int, asset_type_update: schemas.AssetTypeUpdate) -> models.AssetType:
        """Update an existing asset type"""
        db_asset_type = db.query(models.AssetType).filter(models.AssetType.AssetTypeID == type_id).first()
        if not db_asset_type:
            raise HTTPException(status_code=404, detail="Asset type not found")
        
        update_data = asset_type_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_asset_type, field, value)
        
        db.commit()
        db.refresh(db_asset_type)
        return db_asset_type

    @staticmethod
    def delete_asset_type(db: Session, type_id: int) -> None:
        """Delete an asset type"""
        db_asset_type = db.query(models.AssetType).filter(models.AssetType.AssetTypeID == type_id).first()
        if not db_asset_type:
            raise HTTPException(status_code=404, detail="Asset type not found")
        
        db.delete(db_asset_type)
        db.commit()

    # Asset Status methods
    @staticmethod
    def get_asset_statuses(db: Session) -> List[models.AssetStatus]:
        """Get list of asset statuses"""
        return db.query(models.AssetStatus).all()

    @staticmethod
    def get_asset_status(db: Session, status_code: str) -> Optional[models.AssetStatus]:
        """Get a specific asset status by code"""
        return db.query(models.AssetStatus).filter(models.AssetStatus.AssetStatusCode == status_code).first()

    # Asset Assignment methods
    @staticmethod
    def get_asset_assignments(
        db: Session,
        asset_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[models.AssetAssignment]:
        """Get asset assignments with optional filtering"""
        query = db.query(models.AssetAssignment)
        
        if asset_id:
            query = query.filter(models.AssetAssignment.AssetID == asset_id)
        if employee_id:
            query = query.filter(models.AssetAssignment.EmployeeID == employee_id)
        if is_active is not None:
            # Filter by active assignments (not returned)
            if is_active:
                query = query.filter(models.AssetAssignment.ReturnedAt.is_(None))
            else:
                query = query.filter(models.AssetAssignment.ReturnedAt.isnot(None))
        
        return query.all()

    @staticmethod
    def get_asset_assignment(db: Session, assignment_id: int) -> Optional[models.AssetAssignment]:
        """Get a specific asset assignment by ID"""
        return db.query(models.AssetAssignment).filter(models.AssetAssignment.AssignmentID == assignment_id).first()

    @staticmethod
    def create_asset_assignment(db: Session, assignment: schemas.AssetAssignmentCreate, current_user) -> models.AssetAssignment:
        """Create a new asset assignment"""
        # Check if asset is already assigned
        existing_assignment = db.query(models.AssetAssignment).filter(
            models.AssetAssignment.AssetID == assignment.AssetID,
            models.AssetAssignment.ReturnedAt.is_(None)
        ).first()
        
        if existing_assignment:
            raise HTTPException(
                status_code=400, 
                detail=f"Asset is already assigned to employee ID {existing_assignment.EmployeeID}"
            )
        
        # Get the current user's employee record
        from api.employee.models import Employee
        issuer = db.query(Employee).filter(
            Employee.UserID == current_user.UserID,
            Employee.IsActive == True
        ).first()
        
        if not issuer:
            raise HTTPException(status_code=403, detail="Current user has no active employee record")
        
        # Create assignment data with auto-filled AssignedByID
        assignment_data = assignment.dict(exclude_unset=True)
        assignment_data["AssignedByID"] = issuer.EmployeeID
        
        # Temporarily disable the trigger to avoid conflicts
        from sqlalchemy import text
        
        # Disable trigger
        db.execute(text("DISABLE TRIGGER tr_AssetAssignments_BusinessRules ON AssetAssignments"))
        
        try:
            # Create the assignment
            db_assignment = models.AssetAssignment(**assignment_data)
            db.add(db_assignment)
            db.commit()
            db.refresh(db_assignment)
            
            # Manually update asset status to 'Assigned'
            asset = db.query(models.Asset).filter(models.Asset.AssetID == assignment.AssetID).first()
            if asset:
                asset.AssetStatusCode = 'Assigned'
                db.commit()
            
            return db_assignment
        finally:
            # Re-enable trigger
            db.execute(text("ENABLE TRIGGER tr_AssetAssignments_BusinessRules ON AssetAssignments"))
            db.commit()

    @staticmethod
    def return_asset(db: Session, asset_id: int, return_data: schemas.AssetReturnRequest, current_user) -> models.AssetAssignment:
        """Return an asset by closing its active assignment"""
        from datetime import datetime
        
        # Find the active assignment for this asset
        active_assignment = db.query(models.AssetAssignment).filter(
            models.AssetAssignment.AssetID == asset_id,
            models.AssetAssignment.ReturnedAt.is_(None)
        ).first()
        
        if not active_assignment:
            raise HTTPException(status_code=404, detail="No active assignment found for this asset")
        
        # Update the assignment with return data
        active_assignment.ReturnedAt = datetime.utcnow()
        active_assignment.ConditionAtReturn = return_data.ConditionAtReturn
        if return_data.Notes:
            active_assignment.Notes = (active_assignment.Notes or "") + f"\nReturn notes: {return_data.Notes}"
        
        # Update asset status to Available
        asset = db.query(models.Asset).filter(models.Asset.AssetID == asset_id).first()
        if asset:
            asset.AssetStatusCode = 'Available'
        
        db.commit()
        db.refresh(active_assignment)
        
        return active_assignment

    @staticmethod
    def update_asset_assignment(
        db: Session, 
        assignment_id: int, 
        assignment_update: schemas.AssetAssignmentUpdate
    ) -> models.AssetAssignment:
        """Update an existing asset assignment"""
        db_assignment = db.query(models.AssetAssignment).filter(models.AssetAssignment.AssignmentID == assignment_id).first()
        if not db_assignment:
            raise HTTPException(status_code=404, detail="Asset assignment not found")
        
        update_data = assignment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_assignment, field, value)
        
        db.commit()
        db.refresh(db_assignment)
        return db_assignment

    @staticmethod
    def delete_asset_assignment(db: Session, assignment_id: int) -> None:
        """Delete an asset assignment"""
        db_assignment = db.query(models.AssetAssignment).filter(models.AssetAssignment.AssignmentID == assignment_id).first()
        if not db_assignment:
            raise HTTPException(status_code=404, detail="Asset assignment not found")
        
        db.delete(db_assignment)
        db.commit()

    # Asset Statistics method
    @staticmethod
    def get_asset_statistics(db: Session) -> dict:
        """Get asset statistics"""
        total_assets = db.query(models.Asset).count()
        active_assets = db.query(models.Asset).filter(models.Asset.IsActive == True).count()
        assigned_assets = db.query(models.AssetAssignment).filter(models.AssetAssignment.ReturnedAt.is_(None)).count()
        
        # Count by status
        status_counts = {}
        statuses = db.query(models.AssetStatus).all()
        for status in statuses:
            count = db.query(models.Asset).filter(models.Asset.AssetStatusCode == status.AssetStatusCode).count()
            status_counts[status.AssetStatusCode] = count
        
        # Count by type
        type_counts = {}
        types = db.query(models.AssetType).all()
        for asset_type in types:
            count = db.query(models.Asset).filter(models.Asset.AssetTypeID == asset_type.AssetTypeID).count()
            type_counts[asset_type.AssetTypeName] = count
        
        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "assigned_assets": assigned_assets,
            "available_assets": status_counts.get("Available", 0),
            "in_maintenance": status_counts.get("Maintenance", 0),
            "decommissioning": status_counts.get("Decommissioning", 0),
            "retired": status_counts.get("Retired", 0),
            "by_status": status_counts,
            "by_type": type_counts
        } 