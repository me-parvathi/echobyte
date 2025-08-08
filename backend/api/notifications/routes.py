from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from core.database import get_db
from core.auth import get_current_user
from core.notification_service import NotificationService
from core.notification_worker import deliver_desktop_notification
from core.models import NotificationDelivery
from api.notifications.schemas import (
    NotificationCreate,
    NotificationRead,
    UserNotificationPreferenceRead,
    UserNotificationPreferenceUpdate
)
from api.auth.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/", response_model=NotificationRead)
async def create_notification(
    data: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification."""
    try:
        service = NotificationService(db)
        notification = await service.create_notification(data)
        
        # Get the desktop delivery record to trigger background delivery
        desktop_delivery = db.query(NotificationDelivery).filter(
            and_(
                NotificationDelivery.NotificationID == notification.Id,
                NotificationDelivery.Channel == 'desktop'
            )
        ).first()
        
        if desktop_delivery:
            background_tasks.add_task(
                deliver_desktop_notification, 
                desktop_delivery.Id, 
                None  # Let the worker create its own session
            )
        
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")


@router.get("/", response_model=List[NotificationRead])
async def list_user_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notifications for the current user."""
    try:
        service = NotificationService(db)
        notifications = await service.list_user_notifications(
            user_id=current_user.UserID,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list notifications: {str(e)}")


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications for the current user."""
    try:
        service = NotificationService(db)
        count = await service.unread_count(current_user.UserID)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    try:
        service = NotificationService(db)
        success = await service.mark_as_read(notification_id, current_user.UserID)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Notification not found or does not belong to current user"
            )
        
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@router.put("/preferences", response_model=UserNotificationPreferenceRead)
async def upsert_user_preferences(
    preferences: UserNotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences."""
    try:
        # Get existing preferences or create new ones
        from core.models import UserNotificationPreference
        
        existing_prefs = db.query(UserNotificationPreference).filter(
            UserNotificationPreference.UserID == current_user.UserID
        ).first()
        
        if existing_prefs:
            # Update existing preferences
            for field, value in preferences.dict(exclude_unset=True).items():
                setattr(existing_prefs, field, value)
            existing_prefs.UpdatedAt = db.query(func.getutcdate()).scalar()
        else:
            # Create new preferences
            prefs_data = preferences.dict(exclude_unset=True)
            prefs_data["UserID"] = current_user.UserID
            existing_prefs = UserNotificationPreference(**prefs_data)
            db.add(existing_prefs)
        
        db.commit()
        db.refresh(existing_prefs)
        return existing_prefs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/preferences", response_model=UserNotificationPreferenceRead)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user notification preferences."""
    try:
        from core.models import UserNotificationPreference
        
        preferences = db.query(UserNotificationPreference).filter(
            UserNotificationPreference.UserID == current_user.UserID
        ).first()
        
        if not preferences:
            # Return default preferences if none exist
            preferences = UserNotificationPreference(
                UserID=current_user.UserID,
                EmailEnabled=True,
                PushEnabled=True,
                DesktopEnabled=True,
                SoundEnabled=True,
                Timezone="UTC"
            )
        
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}") 