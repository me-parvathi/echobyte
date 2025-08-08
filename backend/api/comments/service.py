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
        
        # Create notifications for relevant users
        self._create_comment_notifications(db, entity_type, entity_id, comment, commenter_id)
        
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
    
    def _create_comment_notifications(self, db: Session, entity_type: str, entity_id: int, comment: Comment, commenter_id: int):
        """Create notifications for relevant users when a comment is added"""
        try:
            import uuid
            from datetime import datetime, timedelta
            from core.models import Notification, NotificationDelivery
            
            if entity_type == "LeaveApplication":
                # Get the leave application
                leave_app = db.query(LeaveApplication).filter(
                    LeaveApplication.LeaveApplicationID == entity_id
                ).first()
                
                if not leave_app:
                    return
                
                # Get the employee who applied for leave
                from api.employee.models import Employee
                applicant = db.query(Employee).filter(
                    Employee.EmployeeID == leave_app.EmployeeID
                ).first()
                
                if not applicant:
                    return
                
                # Get the commenter info
                commenter = db.query(Employee).filter(
                    Employee.EmployeeID == commenter_id
                ).first()
                
                commenter_name = f"{commenter.FirstName} {commenter.LastName}" if commenter else "Someone"
                
                # Create notification for the leave applicant (if they're not the commenter)
                if applicant.EmployeeID != commenter_id:
                    notification = Notification(
                        Id=str(uuid.uuid4()),
                        UserID=applicant.UserID,
                        Type="comment",
                        Category="leave",
                        Title="New comment on your leave application",
                        Message=f"{commenter_name} commented: {comment.CommentText[:100]}{'...' if len(comment.CommentText) > 100 else ''}",
                        Priority="normal",
                        Metadata=f"leave_application:{entity_id}",
                        ExpiresAt=datetime.utcnow() + timedelta(days=30),
                        IsRead=False,
                        CreatedAt=datetime.utcnow()
                    )
                    
                    db.add(notification)
                    
                    # Create desktop delivery record
                    delivery = NotificationDelivery(
                        Id=str(uuid.uuid4()),
                        NotificationID=notification.Id,
                        Channel='desktop',
                        Status='pending',
                        RetryCount=0,
                        MaxRetries=3,
                        CreatedAt=datetime.utcnow()
                    )
                    
                    db.add(delivery)
                
                # Create notification for the manager (if they exist and are not the commenter)
                if leave_app.ManagerID and leave_app.ManagerID != commenter_id:
                    manager = db.query(Employee).filter(
                        Employee.EmployeeID == leave_app.ManagerID
                    ).first()
                    
                    if manager:
                        notification = Notification(
                            Id=str(uuid.uuid4()),
                            UserID=manager.UserID,
                            Type="comment",
                            Category="leave",
                            Title="New comment on leave application",
                            Message=f"{commenter_name} commented on {applicant.FirstName}'s leave application: {comment.CommentText[:100]}{'...' if len(comment.CommentText) > 100 else ''}",
                            Priority="normal",
                            Metadata=f"leave_application:{entity_id}",
                            ExpiresAt=datetime.utcnow() + timedelta(days=30),
                            IsRead=False,
                            CreatedAt=datetime.utcnow()
                        )
                        
                        db.add(notification)
                        
                        # Create desktop delivery record
                        delivery = NotificationDelivery(
                            Id=str(uuid.uuid4()),
                            NotificationID=notification.Id,
                            Channel='desktop',
                            Status='pending',
                            RetryCount=0,
                            MaxRetries=3,
                            CreatedAt=datetime.utcnow()
                        )
                        
                        db.add(delivery)
                
                # Commit all notifications
                db.commit()
                        
        except Exception as e:
            # Log the error but don't fail the comment creation
            print(f"Failed to create comment notifications: {e}")
            # Rollback the notification creation but keep the comment
            db.rollback()
    
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