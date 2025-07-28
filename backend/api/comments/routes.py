from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.auth import get_current_user
from api.employee.models import Employee
from .schemas import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from .service import CommentService
from .repository import CommentRepository

router = APIRouter()

# Dependency injection
def get_comment_repository() -> CommentRepository:
    return CommentRepository()

def get_comment_service(repository: CommentRepository = Depends(get_comment_repository)) -> CommentService:
    return CommentService(repository)

@router.get("/{entity_type}/{entity_id}", response_model=CommentListResponse)
async def get_comments_for_entity(
    entity_type: str,
    entity_id: int,
    comment_service: CommentService = Depends(get_comment_service),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a specific entity.
    
    Currently supported entity types:
    - LeaveApplication: Comments on leave applications
    - Ticket: Comments on tickets
    """
    return comment_service.get_comments_for_entity(db, entity_type, entity_id)

@router.post("/{entity_type}/{entity_id}", response_model=CommentResponse)
async def create_comment_for_entity(
    entity_type: str,
    entity_id: int,
    comment_data: CommentCreate,
    comment_service: CommentService = Depends(get_comment_service),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a comment for a specific entity.
    
    Currently supported entity types:
    - LeaveApplication: Comments on leave applications
    - Ticket: Comments on tickets
    """
    return comment_service.create_comment(
        db, entity_type, entity_id, comment_data, current_user.EmployeeID
    )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    comment_service: CommentService = Depends(get_comment_service),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing comment.
    
    Users can only edit their own comments.
    """
    return comment_service.update_comment(db, comment_id, comment_data, current_user.EmployeeID)

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    comment_service: CommentService = Depends(get_comment_service),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment.
    
    Users can only delete their own comments.
    """
    success = comment_service.delete_comment(db, comment_id, current_user.EmployeeID)
    if success:
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found") 