import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime

from core.models import Notification, NotificationDelivery, LearningNotification
from api.notifications.schemas import NotificationCreate, LearningNotificationCreate


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_notification(self, data: NotificationCreate) -> Notification:
        """Create a new notification with desktop delivery record."""
        # Create notification
        notification = Notification(
            Id=str(uuid.uuid4()),
            UserID=data.user_id,
            Type=data.type,
            Category=data.category,
            Title=data.title,
            Message=data.message,
            Priority=data.priority,
            Metadata=data.metadata,
            ExpiresAt=data.expires_at,
            IsRead=False,
            CreatedAt=datetime.utcnow()
        )
        
        self.db.add(notification)
        
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
        
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification

    async def list_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """List notifications for a user with optional filtering."""
        query = self.db.query(Notification).filter(Notification.UserID == user_id)
        
        if unread_only:
            query = query.filter(Notification.IsRead == False)
        
        notifications = query.order_by(desc(Notification.CreatedAt)).offset(offset).limit(limit).all()
        return notifications

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read for the specified user."""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.Id == notification_id,
                Notification.UserID == user_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.IsRead = True
        notification.ReadAt = datetime.utcnow()
        
        self.db.commit()
        return True

    async def unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user."""
        count = self.db.query(Notification).filter(
            and_(
                Notification.UserID == user_id,
                Notification.IsRead == False
            )
        ).count()
        
        return count

    async def create_learning_notification(
        self,
        learning_data: LearningNotificationCreate
    ) -> LearningNotification:
        """Create a learning notification record."""
        learning_notification = LearningNotification(
            Id=str(uuid.uuid4()),
            NotificationID=learning_data.notification_id,
            CourseID=learning_data.course_id,
            ActionType=learning_data.action_type,
            CourseName=learning_data.course_name,
            ProgressPercentage=learning_data.progress_percentage,
            CreatedAt=datetime.utcnow()
        )
        
        self.db.add(learning_notification)
        self.db.commit()
        self.db.refresh(learning_notification)
        
        return learning_notification 