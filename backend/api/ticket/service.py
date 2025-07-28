from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from . import models, schemas
from fastapi import HTTPException, status
from api.employee.models import Employee
from api.asset.models import Asset
from core.pagination import paginate_query

class TicketService:
    
    @staticmethod
    def validate_priority_code(db: Session, priority_code: str) -> bool:
        """Validate that priority code exists in lookup table"""
        # Use case-sensitive comparison to avoid database collation issues
        from sqlalchemy import text
        query = text("""
            SELECT * FROM TicketPriorities 
            WHERE PriorityCode COLLATE SQL_Latin1_General_CP1_CS_AS = :priority_code 
            AND IsActive = 1
        """)
        result = db.execute(query, {"priority_code": priority_code}).fetchone()
        return result is not None
    
    @staticmethod
    def validate_status_code(db: Session, status_code: str) -> bool:
        """Validate that status code exists in lookup table"""
        # Use case-sensitive comparison to avoid database collation issues
        from sqlalchemy import text
        query = text("""
            SELECT * FROM TicketStatuses 
            WHERE TicketStatusCode COLLATE SQL_Latin1_General_CP1_CS_AS = :status_code 
            AND IsActive = 1
        """)
        result = db.execute(query, {"status_code": status_code}).fetchone()
        return result is not None
    
    @staticmethod
    def validate_category_id(db: Session, category_id: int) -> bool:
        """Validate that category ID exists in lookup table"""
        category = db.query(models.TicketCategory).filter(
            models.TicketCategory.CategoryID == category_id,
            models.TicketCategory.IsActive == True
        ).first()
        return category is not None
    
    @staticmethod
    def validate_employee_id(db: Session, employee_id: int) -> bool:
        """Validate that employee ID exists"""
        employee = db.query(Employee).filter(
            Employee.EmployeeID == employee_id,
            Employee.IsActive == True
        ).first()
        return employee is not None
    
    @staticmethod
    def validate_asset_id(db: Session, asset_id: int) -> bool:
        """Validate that asset ID exists"""
        asset = db.query(Asset).filter(
            Asset.AssetID == asset_id,
            Asset.IsActive == True
        ).first()
        return asset is not None
    
    @staticmethod
    def generate_ticket_number(db: Session) -> str:
        """Generate unique ticket number in format TKT-YYYY-NNNN"""
        year = datetime.now().year
        # Get the last ticket number for this year
        last_ticket = db.query(models.Ticket).filter(
            models.Ticket.TicketNumber.like(f"TKT-{year}-%")
        ).order_by(models.Ticket.TicketNumber.desc()).first()
        
        if last_ticket:
            # Extract the number part and increment
            try:
                last_number = int(last_ticket.TicketNumber.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"TKT-{year}-{new_number:04d}"
    
    @staticmethod
    def calculate_due_date(priority_code: str, db: Session) -> datetime:
        """Calculate due date based on priority SLA"""
        if not TicketService.validate_priority_code(db, priority_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority code: {priority_code}"
            )
        
        # Use case-sensitive comparison to avoid database collation issues
        from sqlalchemy import text
        query = text("""
            SELECT * FROM TicketPriorities 
            WHERE PriorityCode COLLATE SQL_Latin1_General_CP1_CS_AS = :priority_code
        """)
        priority_result = db.execute(query, {"priority_code": priority_code}).fetchone()
        if not priority_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority code: {priority_code}"
            )
        
        # Convert result to model object for compatibility
        priority = models.TicketPriority(
            PriorityCode=priority_result.PriorityCode,
            PriorityName=priority_result.PriorityName,
            SLAHours=priority_result.SLAHours,
            IsActive=priority_result.IsActive,
            CreatedAt=priority_result.CreatedAt
        )
        
        # Calculate due date based on SLA hours
        due_date = datetime.now() + timedelta(hours=priority.SLAHours)
        return due_date
    
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
        return db.query(models.Ticket).filter(models.Ticket.TicketID == ticket_id).first()
    
    @staticmethod
    def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[models.Ticket]:
        return db.query(models.Ticket).filter(models.Ticket.TicketNumber == ticket_number).first()
    
    @staticmethod
    def get_tickets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status_code: Optional[str] = None,
        priority_code: Optional[str] = None,
        category_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        opened_by_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        query = db.query(models.Ticket)
        
        if status_code:
            query = query.filter(models.Ticket.StatusCode == status_code)
        
        if priority_code:
            query = query.filter(models.Ticket.PriorityCode == priority_code)
        
        if category_id:
            query = query.filter(models.Ticket.CategoryID == category_id)
        
        if assigned_to_id:
            query = query.filter(models.Ticket.AssignedToID == assigned_to_id)
        
        if opened_by_id:
            query = query.filter(models.Ticket.OpenedByID == opened_by_id)
        
        if asset_id:
            query = query.filter(models.Ticket.AssetID == asset_id)
        
        if is_active is not None:
            # For tickets, we consider active as not closed
            if is_active:
                query = query.filter(models.Ticket.StatusCode.notin_(["Closed", "Cancelled"]))
            else:
                query = query.filter(models.Ticket.StatusCode.in_(["Closed", "Cancelled"]))
        
        return paginate_query(query, skip, limit, models.Ticket.CreatedAt)
    
    @staticmethod
    def create_ticket(db: Session, ticket: schemas.TicketCreate, opened_by_id: int) -> models.Ticket:
        # Validate lookup table references
        if not TicketService.validate_priority_code(db, ticket.PriorityCode):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority code: {ticket.PriorityCode}"
            )
        
        if not TicketService.validate_status_code(db, ticket.StatusCode):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status code: {ticket.StatusCode}"
            )
        
        if not TicketService.validate_category_id(db, ticket.CategoryID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category ID: {ticket.CategoryID}"
            )
        
        # Validate employee references
        if not TicketService.validate_employee_id(db, opened_by_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid opened by employee ID: {opened_by_id}"
            )
        
        if ticket.AssignedToID and not TicketService.validate_employee_id(db, ticket.AssignedToID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid assigned to employee ID: {ticket.AssignedToID}"
            )
        
        if ticket.EscalatedToID and not TicketService.validate_employee_id(db, ticket.EscalatedToID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid escalated to employee ID: {ticket.EscalatedToID}"
            )
        
        # Validate asset reference if provided
        if ticket.AssetID and not TicketService.validate_asset_id(db, ticket.AssetID):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset ID: {ticket.AssetID}"
            )
        
        # Generate ticket number
        ticket_number = TicketService.generate_ticket_number(db)
        
        # Calculate due date
        due_date = TicketService.calculate_due_date(ticket.PriorityCode, db)
        
        # Create ticket
        ticket_data = ticket.dict()
        ticket_data['TicketNumber'] = ticket_number
        ticket_data['OpenedByID'] = opened_by_id
        ticket_data['DueDate'] = due_date
        
        db_ticket = models.Ticket(**ticket_data)
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        # Log activity
        TicketActivityService.log_activity(
            db, db_ticket.TicketID, opened_by_id, "Ticket_Created", 
            None, ticket_number, "Ticket created"
        )
        
        return db_ticket
    
    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_update: schemas.TicketUpdate) -> Optional[models.Ticket]:
        db_ticket = TicketService.get_ticket(db, ticket_id)
        if not db_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        update_data = ticket_update.dict(exclude_unset=True)
        
        # Validate lookup table references if they're being updated
        if 'PriorityCode' in update_data:
            if not TicketService.validate_priority_code(db, update_data['PriorityCode']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority code: {update_data['PriorityCode']}"
                )
        
        if 'StatusCode' in update_data:
            if not TicketService.validate_status_code(db, update_data['StatusCode']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status code: {update_data['StatusCode']}"
                )
        
        if 'CategoryID' in update_data:
            if not TicketService.validate_category_id(db, update_data['CategoryID']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category ID: {update_data['CategoryID']}"
                )
        
        # Validate employee references if they're being updated
        if 'AssignedToID' in update_data and update_data['AssignedToID']:
            if not TicketService.validate_employee_id(db, update_data['AssignedToID']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid assigned to employee ID: {update_data['AssignedToID']}"
                )
        
        if 'EscalatedToID' in update_data and update_data['EscalatedToID']:
            if not TicketService.validate_employee_id(db, update_data['EscalatedToID']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid escalated to employee ID: {update_data['EscalatedToID']}"
                )
        
        # Validate asset reference if it's being updated
        if 'AssetID' in update_data and update_data['AssetID']:
            if not TicketService.validate_asset_id(db, update_data['AssetID']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid asset ID: {update_data['AssetID']}"
                )
        
        # Handle status changes
        if 'StatusCode' in update_data:
            old_status = db_ticket.StatusCode
            new_status = update_data['StatusCode']
            
            # Update timestamps based on status
            if new_status == "Assigned" and old_status == "Open":
                update_data['AssignedAt'] = datetime.now()
            elif new_status == "In-Progress" and old_status == "Assigned":
                pass  # No specific timestamp
            elif new_status == "Resolved":
                update_data['ResolvedAt'] = datetime.now()
            elif new_status == "Closed":
                update_data['ClosedAt'] = datetime.now()
            elif new_status == "Escalated":
                update_data['EscalatedAt'] = datetime.now()
        
        # Handle priority changes - recalculate due date
        if 'PriorityCode' in update_data:
            due_date = TicketService.calculate_due_date(update_data['PriorityCode'], db)
            update_data['DueDate'] = due_date
        
        # Update ticket
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        
        db.commit()
        db.refresh(db_ticket)
        
        # Log activity for significant changes
        if 'StatusCode' in update_data:
            TicketActivityService.log_activity(
                db, ticket_id, db_ticket.OpenedByID, "Status_Change",
                old_status, update_data['StatusCode'], f"Status changed from {old_status} to {update_data['StatusCode']}"
            )
        
        if 'AssignedToID' in update_data:
            TicketActivityService.log_activity(
                db, ticket_id, db_ticket.OpenedByID, "Assignment",
                None, str(update_data['AssignedToID']), "Ticket assigned"
            )
        
        return db_ticket
    
    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        db_ticket = TicketService.get_ticket(db, ticket_id)
        if not db_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Soft delete by setting status to Cancelled
        db_ticket.StatusCode = "Cancelled"
        db_ticket.ClosedAt = datetime.now()
        db.commit()
        
        return True
    
    @staticmethod
    def get_ticket_statistics(db: Session) -> Dict[str, Any]:
        """Get ticket statistics for dashboard"""
        total_tickets = db.query(models.Ticket).count()
        
        # Status counts
        status_counts = db.query(
            models.Ticket.StatusCode,
            func.count(models.Ticket.TicketID).label('count')
        ).group_by(models.Ticket.StatusCode).all()
        
        # Priority counts
        priority_counts = db.query(
            models.Ticket.PriorityCode,
            func.count(models.Ticket.TicketID).label('count')
        ).group_by(models.Ticket.PriorityCode).all()
        
        # Overdue tickets
        overdue_tickets = db.query(models.Ticket).filter(
            and_(
                models.Ticket.DueDate < datetime.now(),
                models.Ticket.StatusCode.notin_(["Closed", "Cancelled", "Resolved"])
            )
        ).count()
        
        return {
            "total_tickets": total_tickets,
            "status_counts": {status: count for status, count in status_counts},
            "priority_counts": {priority: count for priority, count in priority_counts},
            "overdue_tickets": overdue_tickets
        }

class TicketActivityService:
    
    @staticmethod
    def log_activity(
        db: Session, 
        ticket_id: int, 
        performed_by_id: int, 
        activity_type: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        details: Optional[str] = None
    ) -> models.TicketActivity:
        """Log an activity for a ticket"""
        activity = models.TicketActivity(
            TicketID=ticket_id,
            ActivityType=activity_type,
            PerformedByID=performed_by_id,
            OldValue=old_value,
            NewValue=new_value,
            ActivityDetails=details
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_ticket_activities(db: Session, ticket_id: int) -> List[models.TicketActivity]:
        """Get all activities for a ticket"""
        return db.query(models.TicketActivity).filter(
            models.TicketActivity.TicketID == ticket_id
        ).order_by(models.TicketActivity.PerformedAt.desc()).all()

class TicketAttachmentService:
    
    @staticmethod
    def create_attachment(
        db: Session, 
        ticket_id: int, 
        uploaded_by_id: int,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: Optional[str] = None
    ) -> models.TicketAttachment:
        """Create a new attachment for a ticket"""
        attachment = models.TicketAttachment(
            TicketID=ticket_id,
            UploadedByID=uploaded_by_id,
            FileName=file_name,
            FilePath=file_path,
            FileSize=file_size,
            MimeType=mime_type
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        # Log activity
        TicketActivityService.log_activity(
            db, ticket_id, uploaded_by_id, "Attachment_Added",
            None, file_name, f"File attached: {file_name}"
        )
        
        return attachment
    
    @staticmethod
    def get_ticket_attachments(db: Session, ticket_id: int) -> List[models.TicketAttachment]:
        """Get all attachments for a ticket"""
        return db.query(models.TicketAttachment).filter(
            models.TicketAttachment.TicketID == ticket_id
        ).order_by(models.TicketAttachment.UploadedAt.desc()).all()
    
    @staticmethod
    def delete_attachment(db: Session, attachment_id: int) -> bool:
        """Delete an attachment"""
        attachment = db.query(models.TicketAttachment).filter(
            models.TicketAttachment.AttachmentID == attachment_id
        ).first()
        
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        
        db.delete(attachment)
        db.commit()
        
        # Log activity
        TicketActivityService.log_activity(
            db, attachment.TicketID, attachment.UploadedByID, "Attachment_Removed",
            attachment.FileName, None, f"File removed: {attachment.FileName}"
        )
        
        return True

class LookupService:
    
    @staticmethod
    def get_ticket_statuses(db: Session) -> List[models.TicketStatus]:
        return db.query(models.TicketStatus).filter(models.TicketStatus.IsActive == True).all()
    
    @staticmethod
    def get_ticket_priorities(db: Session) -> List[models.TicketPriority]:
        return db.query(models.TicketPriority).filter(models.TicketPriority.IsActive == True).all()
    
    @staticmethod
    def get_ticket_categories(db: Session, include_inactive: bool = False) -> List[models.TicketCategory]:
        query = db.query(models.TicketCategory)
        if not include_inactive:
            query = query.filter(models.TicketCategory.IsActive == True)
        return query.all()
    
    @staticmethod
    def get_category_hierarchy(db: Session) -> List[models.TicketCategory]:
        """Get categories in hierarchical structure"""
        # Get root categories (no parent)
        root_categories = db.query(models.TicketCategory).filter(
            and_(
                models.TicketCategory.ParentCategoryID.is_(None),
                models.TicketCategory.IsActive == True
            )
        ).all()
        return root_categories

class AssetIntegrationService:
    
    @staticmethod
    def get_user_assigned_assets(db: Session, user_id: int) -> List[Asset]:
        """Get all assets assigned to a specific user"""
        from api.asset.models import AssetAssignment
        
        # Get active asset assignments for the user
        assignments = db.query(AssetAssignment).filter(
            and_(
                AssetAssignment.EmployeeID == user_id,
                AssetAssignment.ReturnedAt.is_(None)  # Active assignments only
            )
        ).all()
        
        # Get the actual asset details
        asset_ids = [assignment.AssetID for assignment in assignments]
        assets = db.query(Asset).filter(Asset.AssetID.in_(asset_ids)).all()
        
        return assets
    
    @staticmethod
    def get_community_assets_by_location(db: Session, user_location_id: int) -> List[Asset]:
        """Get community assets available in user's location"""
        # TODO: Implement community asset logic
        # This would include:
        # - Shared printers in the location
        # - Conference room equipment
        # - Common area devices
        # - Network infrastructure
        return []
    
    @staticmethod
    def get_assets_for_category(db: Session, category_id: int, user_id: int) -> List[Asset]:
        """Get relevant assets based on ticket category and user"""
        # Get user's assigned assets
        user_assets = AssetIntegrationService.get_user_assigned_assets(db, user_id)
        
        # TODO: Filter by category if needed
        # For now, return all user assets
        return user_assets
    
    @staticmethod
    def get_asset_selection_options(db: Session, user_id: int, category_id: Optional[int] = None) -> schemas.AssetSelectionResponse:
        """Get asset selection options for ticket creation"""
        from api.asset.models import AssetType
        from api.location.models import Location
        
        # Get user's assigned assets
        user_assets = AssetIntegrationService.get_user_assigned_assets(db, user_id)
        
        # Convert to selection options
        personal_assets = []
        for asset in user_assets:
            # Get asset type and location names
            asset_type = db.query(AssetType).filter(AssetType.AssetTypeID == asset.AssetTypeID).first()
            location = db.query(Location).filter(Location.LocationID == asset.LocationID).first()
            
            personal_assets.append(schemas.AssetSelectionOption(
                AssetID=asset.AssetID,
                AssetTag=asset.AssetTag,
                AssetTypeName=asset_type.AssetTypeName if asset_type else "Unknown",
                LocationName=location.LocationName if location else "Unknown",
                IsAssignedToUser=True,
                AssignmentType="Personal"
            ))
        
        # TODO: Get community assets
        # This would include shared assets in user's location
        community_assets = []
        
        return schemas.AssetSelectionResponse(
            personal_assets=personal_assets,
            community_assets=community_assets,
            total_assets=len(personal_assets) + len(community_assets)
        )
    
    @staticmethod
    def validate_asset_access(db: Session, asset_id: int, user_id: int) -> bool:
        """Validate if user has access to report issues for this asset"""
        # Check if asset is assigned to user
        user_assets = AssetIntegrationService.get_user_assigned_assets(db, user_id)
        user_asset_ids = [asset.AssetID for asset in user_assets]
        
        if asset_id in user_asset_ids:
            return True
        
        # TODO: Check community asset access
        # - Location-based access
        # - Public asset access
        # - Role-based permissions
        
        return False
    
    @staticmethod
    def link_ticket_to_asset(db: Session, ticket_id: int, asset_id: int, user_id: int) -> models.Ticket:
        """Link a ticket to an asset with access validation"""
        ticket = TicketService.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Validate asset exists using the validation method
        if not TicketService.validate_asset_id(db, asset_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset ID: {asset_id}"
            )
        
        # Validate user has access to this asset
        if not AssetIntegrationService.validate_asset_access(db, asset_id, user_id):
            raise HTTPException(status_code=403, detail="You don't have access to report issues for this asset")
        
        # Get asset for logging
        asset = db.query(Asset).filter(Asset.AssetID == asset_id).first()
        
        ticket.AssetID = asset_id
        db.commit()
        db.refresh(ticket)
        
        # Log activity
        TicketActivityService.log_activity(
            db, ticket_id, ticket.OpenedByID, "Asset_Linked",
            None, str(asset_id), f"Linked to asset: {asset.AssetTag}"
        )
        
        return ticket
    
    @staticmethod
    def get_tickets_for_asset(db: Session, asset_id: int) -> List[models.Ticket]:
        """Get all tickets related to an asset"""
        return db.query(models.Ticket).filter(
            models.Ticket.AssetID == asset_id
        ).order_by(models.Ticket.CreatedAt.desc()).all()
    
    @staticmethod
    def create_asset_ticket(
        db: Session, 
        asset_id: int, 
        subject: str, 
        description: str,
        category_id: int,
        priority_code: str,
        opened_by_id: int
    ) -> models.Ticket:
        """Create a ticket specifically for an asset issue"""
        # Validate asset access
        if not AssetIntegrationService.validate_asset_access(db, asset_id, opened_by_id):
            raise HTTPException(status_code=403, detail="You don't have access to report issues for this asset")
        
        ticket_data = schemas.TicketCreate(
            Subject=subject,
            Description=description,
            CategoryID=category_id,
            PriorityCode=priority_code,
            StatusCode="Open",
            AssetID=asset_id
        )
        
        return TicketService.create_ticket(db, ticket_data, opened_by_id) 