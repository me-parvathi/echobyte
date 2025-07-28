from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service
import os
import shutil
from datetime import datetime

router = APIRouter()

# Ticket routes
@router.get("/", response_model=schemas.TicketListResponse)
def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_code: Optional[str] = None,
    priority_code: Optional[str] = None,
    category_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    opened_by_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of tickets with optional filtering"""
    return service.TicketService.get_tickets(
        db, skip=skip, limit=limit,
        status_code=status_code,
        priority_code=priority_code,
        category_id=category_id,
        assigned_to_id=assigned_to_id,
        opened_by_id=opened_by_id,
        asset_id=asset_id,
        is_active=is_active
    )

@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a specific ticket by ID"""
    ticket = service.TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/number/{ticket_number}", response_model=schemas.TicketResponse)
def get_ticket_by_number(ticket_number: str, db: Session = Depends(get_db)):
    """Get a specific ticket by ticket number"""
    ticket = service.TicketService.get_ticket_by_number(db, ticket_number)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/", response_model=schemas.TicketResponse, status_code=201)
def create_ticket(
    ticket: schemas.TicketCreate, 
    opened_by_id: int = Query(..., description="ID of the employee opening the ticket"),
    db: Session = Depends(get_db)
):
    """Create a new ticket with asset validation"""
    # Validate asset access if asset is specified
    if ticket.AssetID:
        if not service.AssetIntegrationService.validate_asset_access(db, ticket.AssetID, opened_by_id):
            raise HTTPException(
                status_code=403, 
                detail="You don't have access to report issues for this asset. Please select from your assigned assets or contact IT support."
            )
    
    return service.TicketService.create_ticket(db, ticket, opened_by_id)

@router.put("/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(
    ticket_id: int, 
    ticket_update: schemas.TicketUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing ticket"""
    return service.TicketService.update_ticket(db, ticket_id, ticket_update)

@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Cancel a ticket (soft delete)"""
    service.TicketService.delete_ticket(db, ticket_id)
    return None

@router.get("/{ticket_id}/activities", response_model=List[schemas.TicketActivityResponse])
def get_ticket_activities(ticket_id: int, db: Session = Depends(get_db)):
    """Get all activities for a ticket"""
    activities = service.TicketActivityService.get_ticket_activities(db, ticket_id)
    return activities

@router.post("/{ticket_id}/activities", response_model=schemas.TicketActivityResponse, status_code=201)
def log_ticket_activity(
    ticket_id: int,
    activity: schemas.TicketActivityCreate,
    performed_by_id: int = Query(..., description="ID of the employee performing the activity"),
    db: Session = Depends(get_db)
):
    """Log an activity for a ticket"""
    return service.TicketActivityService.log_activity(
        db, ticket_id, performed_by_id, activity.ActivityType,
        activity.OldValue, activity.NewValue, activity.ActivityDetails
    )

# Attachment routes
@router.get("/{ticket_id}/attachments", response_model=List[schemas.TicketAttachmentResponse])
def get_ticket_attachments(ticket_id: int, db: Session = Depends(get_db)):
    """Get all attachments for a ticket"""
    attachments = service.TicketAttachmentService.get_ticket_attachments(db, ticket_id)
    return attachments

@router.post("/{ticket_id}/attachments", response_model=schemas.TicketAttachmentResponse, status_code=201)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    uploaded_by_id: int = Query(..., description="ID of the employee uploading the file"),
    db: Session = Depends(get_db)
):
    """Upload an attachment for a ticket"""
    # Create upload directory if it doesn't exist
    upload_dir = f"uploads/tickets/{ticket_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create attachment record
    attachment = service.TicketAttachmentService.create_attachment(
        db, ticket_id, uploaded_by_id, file.filename, file_path, 
        file.size, file.content_type
    )
    
    return attachment

@router.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Delete an attachment"""
    service.TicketAttachmentService.delete_attachment(db, attachment_id)
    return None

# Lookup routes
@router.get("/lookup/statuses", response_model=List[schemas.TicketStatusResponse])
def get_ticket_statuses(db: Session = Depends(get_db)):
    """Get all active ticket statuses"""
    return service.LookupService.get_ticket_statuses(db)

@router.get("/lookup/priorities", response_model=List[schemas.TicketPriorityResponse])
def get_ticket_priorities(db: Session = Depends(get_db)):
    """Get all active ticket priorities"""
    return service.LookupService.get_ticket_priorities(db)

@router.get("/lookup/categories", response_model=List[schemas.TicketCategoryResponse])
def get_ticket_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db)
):
    """Get all ticket categories"""
    return service.LookupService.get_ticket_categories(db, include_inactive)

@router.get("/lookup/categories/hierarchy", response_model=List[schemas.TicketCategoryResponse])
def get_category_hierarchy(db: Session = Depends(get_db)):
    """Get categories in hierarchical structure"""
    return service.LookupService.get_category_hierarchy(db)

# Statistics routes
@router.get("/statistics/dashboard")
def get_ticket_statistics(db: Session = Depends(get_db)):
    """Get ticket statistics for dashboard"""
    return service.TicketService.get_ticket_statistics(db)

# Asset selection routes
@router.get("/assets/selection", response_model=schemas.AssetSelectionResponse)
def get_asset_selection_options(
    user_id: int = Query(..., description="ID of the user creating the ticket"),
    category_id: Optional[int] = Query(None, description="Category ID for filtering assets"),
    db: Session = Depends(get_db)
):
    """Get available assets for ticket creation"""
    return service.AssetIntegrationService.get_asset_selection_options(db, user_id, category_id)

@router.get("/assets/user/{user_id}", response_model=List[schemas.AssetSelectionOption])
def get_user_assets(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all assets assigned to a specific user"""
    assets = service.AssetIntegrationService.get_user_assigned_assets(db, user_id)
    
    # Convert to selection options
    from api.asset.models import AssetType
    from api.location.models import Location
    
    selection_options = []
    for asset in assets:
        asset_type = db.query(AssetType).filter(AssetType.AssetTypeID == asset.AssetTypeID).first()
        location = db.query(Location).filter(Location.LocationID == asset.LocationID).first()
        
        selection_options.append(schemas.AssetSelectionOption(
            AssetID=asset.AssetID,
            AssetTag=asset.AssetTag,
            AssetTypeName=asset_type.AssetTypeName if asset_type else "Unknown",
            LocationName=location.LocationName if location else "Unknown",
            IsAssignedToUser=True,
            AssignmentType="Personal"
        ))
    
    return selection_options

# Asset integration routes
@router.post("/{ticket_id}/link-asset/{asset_id}", response_model=schemas.TicketResponse)
def link_ticket_to_asset(
    ticket_id: int, 
    asset_id: int,
    user_id: int = Query(..., description="ID of the user linking the asset"),
    db: Session = Depends(get_db)
):
    """Link a ticket to an asset with access validation"""
    return service.AssetIntegrationService.link_ticket_to_asset(db, ticket_id, asset_id, user_id)

@router.get("/asset/{asset_id}", response_model=List[schemas.TicketResponse])
def get_tickets_for_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get all tickets related to an asset"""
    return service.AssetIntegrationService.get_tickets_for_asset(db, asset_id)

@router.post("/asset/{asset_id}/create", response_model=schemas.TicketResponse, status_code=201)
def create_asset_ticket(
    asset_id: int,
    subject: str = Query(..., description="Ticket subject"),
    description: str = Query(..., description="Ticket description"),
    category_id: int = Query(..., description="Category ID"),
    priority_code: str = Query(..., description="Priority code"),
    opened_by_id: int = Query(..., description="ID of the employee opening the ticket"),
    db: Session = Depends(get_db)
):
    """Create a ticket specifically for an asset issue"""
    return service.AssetIntegrationService.create_asset_ticket(
        db, asset_id, subject, description, category_id, priority_code, opened_by_id
    )

# Category management routes
@router.post("/categories/", response_model=schemas.TicketCategoryResponse, status_code=201)
def create_category(category: schemas.TicketCategoryCreate, db: Session = Depends(get_db)):
    """Create a new ticket category"""
    db_category = models.TicketCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.TicketCategoryResponse)
def update_category(
    category_id: int, 
    category_update: schemas.TicketCategoryUpdate, 
    db: Session = Depends(get_db)
):
    """Update a ticket category"""
    db_category = db.query(models.TicketCategory).filter(
        models.TicketCategory.CategoryID == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

# Import models for category routes
from . import models 