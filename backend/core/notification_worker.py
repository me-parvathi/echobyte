import logging
from datetime import datetime
from sqlalchemy.orm import Session
from core.models import NotificationDelivery
from core.database import SessionLocal

logger = logging.getLogger(__name__)


async def deliver_desktop_notification(delivery_id: str, db: Session = None):
    """
    Simulate desktop notification delivery by updating status from 'pending' to 'delivered'.
    
    Args:
        delivery_id: The ID of the NotificationDelivery record
        db: Database session (optional - will create new session if None)
    """
    # Create new database session if none provided
    if db is None:
        db = SessionLocal()
        should_close_session = True
    else:
        should_close_session = False
    
    try:
        # Fetch the NotificationDelivery row
        delivery = db.query(NotificationDelivery).filter(
            NotificationDelivery.Id == delivery_id
        ).first()
        
        if not delivery:
            logger.warning(f"NotificationDelivery with ID {delivery_id} not found")
            return
        
        if delivery.Status != 'pending':
            logger.info(f"NotificationDelivery {delivery_id} already processed (status: {delivery.Status})")
            return
        
        # Update status and timestamps
        now = datetime.utcnow()
        delivery.Status = 'delivered'
        delivery.SentAt = now
        delivery.DeliveredAt = now
        
        db.commit()
        logger.info(f"Successfully delivered notification {delivery_id}")
        
    except Exception as e:
        logger.error(f"Failed to deliver notification {delivery_id}: {str(e)}")
        # Don't re-raise - background tasks should be fire-and-forget
    finally:
        # Close session if we created it
        if should_close_session and db:
            db.close() 