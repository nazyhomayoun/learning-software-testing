"""Background tasks for the ticketing system.

In a production system, these would run via Celery, RQ, or similar.
For the course, we keep it simple with direct function calls.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ticketer.repositories.event_repository import SQLAlchemyEventRepository
from ticketer.repositories.order_repository import SQLAlchemyOrderRepository
from ticketer.repositories.seat_repository import SQLAlchemySeatRepository
from ticketer.services.email_service import EmailService
from ticketer.services.order_service import OrderService


def release_expired_holds(db: Session, email_service: EmailService | None = None) -> int:
    """
    Background task to release expired order holds.
    
    This would typically run on a schedule (e.g., every 5 minutes).
    
    Args:
        db: Database session
        email_service: Optional email service for notifications
        
    Returns:
        Number of orders released
    """
    order_repo = SQLAlchemyOrderRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    seat_repo = SQLAlchemySeatRepository(db)
    
    order_service = OrderService(
        order_repo=order_repo,
        event_repo=event_repo,
        seat_repo=seat_repo,
        email_service=email_service,
    )
    
    count = order_service.release_expired_holds()
    
    if count > 0:
        print(f"Released {count} expired order holds at {datetime.now(timezone.utc)}")
    
    return count


def send_reminder_emails(db: Session, email_service: EmailService, hours_before: int = 24):
    """
    Send reminder emails for upcoming events.
    
    This would typically run daily.
    
    Args:
        db: Database session
        email_service: Email service for sending
        hours_before: Send reminders for events starting in this many hours
    """
    from datetime import timedelta

    from ticketer.models.event import Event
    from ticketer.models.order import Order, OrderStatus
    
    # Find events starting soon
    cutoff = datetime.now(timezone.utc) + timedelta(hours=hours_before)
    upcoming_events = db.query(Event).filter(
        Event.start_at >= datetime.now(timezone.utc),
        Event.start_at <= cutoff,
    ).all()
    
    for event in upcoming_events:
        # Find confirmed orders for this event
        orders = (
            db.query(Order)
            .join(Order.items)
            .filter(
                Order.status == OrderStatus.CONFIRMED,
            )
            .distinct()
            .all()
        )
        
        for order in orders:
            # In a real system, we'd get the user's email and send a real email
            print(f"Would send reminder email for event {event.name} to user {order.user_id}")
            # email_service.send_reminder_email(user.email, event)


# Example usage in a scheduler (pseudo-code):
# 
# from apscheduler.schedulers.background import BackgroundScheduler
# from ticketer.db.session import SessionLocal
# 
# scheduler = BackgroundScheduler()
# 
# def scheduled_release_holds():
#     db = SessionLocal()
#     try:
#         release_expired_holds(db)
#     finally:
#         db.close()
# 
# scheduler.add_job(scheduled_release_holds, 'interval', minutes=5)
# scheduler.start()

