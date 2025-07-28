from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import CommentRepository
from .schemas import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from .models import Comment
from api.leave.models import LeaveApplication

class CommentService:
    def __init__(self, repository: CommentRepository):
        self.repository = repository
    
    def _validate_entity_exists(self, db: Session, entity_type: str, entity_id: int):
        """Validate that the target entity exists"""
        if entity_type == "LeaveApplication":
            entity = db.query(LeaveApplication).filter(
                LeaveApplication.LeaveApplicationID == entity_id
            ).first()
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LeaveApplication with ID {entity_id} not found"
                )
        elif entity_type == "Ticket":
            from api.ticket.models import Ticket
            entity = db.query(Ticket).filter(
                Ticket.TicketID == entity_id
            ).first()
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket with ID {entity_id} not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entity type '{entity_type}' is not supported. Currently supported: 'LeaveApplication', 'Ticket'"
            )
    
    def get_comments_for_entity(self, db: Session, entity_type: str, entity_id: int) -> CommentListResponse:
        """Get all comments for a specific entity"""
        # Validate entity exists
        self._validate_entity_exists(db, entity_type, entity_id)
        
        # Get comments
        comments = self.repository.get_by_entity(db, entity_type, entity_id)
        
        # Convert to response format
        comment_responses = []
        for comment in comments:
            response = self._to_response(comment)
            comment_responses.append(response)
        
        return CommentListResponse(
            comments=comment_responses,
            total_count=len(comment_responses)
        )
    
    def create_comment(self, db: Session, entity_type: str, entity_id: int, 
                      comment_data: CommentCreate, commenter_id: int) -> CommentResponse:
        """Create a new comment for an entity"""
        # Validate entity exists
        self._validate_entity_exists(db, entity_type, entity_id)
        
        # Create comment
        comment = self.repository.create_comment_for_entity(db, comment_data, entity_type, entity_id, commenter_id)
        
        return self._to_response(comment)
    
    def update_comment(self, db: Session, comment_id: int, 
                      comment_data: CommentUpdate, commenter_id: int) -> CommentResponse:
        """Update an existing comment"""
        comment = self.repository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if user can edit this comment
        if comment.CommenterID != commenter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments"
            )
        
        updated_comment = self.repository.update(db, comment_id, comment_data)
        return self._to_response(updated_comment)
    
    def delete_comment(self, db: Session, comment_id: int, commenter_id: int) -> bool:
        """Delete a comment"""
        comment = self.repository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if user can delete this comment
        if comment.CommenterID != commenter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments"
            )
        
        return self.repository.delete(db, comment_id)
    
    def _to_response(self, comment: Comment) -> CommentResponse:
        """Convert comment model to response schema"""
        return CommentResponse(
            comment_id=comment.CommentID,
            entity_type=comment.EntityType,
            entity_id=comment.EntityID,
            comment_text=comment.CommentText,
            commenter_role=comment.CommenterRole,
            commenter_id=comment.CommenterID,
            commenter_name=f"{comment.commenter.FirstName} {comment.commenter.LastName}",
            created_at=comment.CreatedAt,
            updated_at=comment.UpdatedAt,
            is_edited=comment.IsEdited,
            is_active=comment.IsActive
        ) 