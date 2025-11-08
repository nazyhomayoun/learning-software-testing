"""API dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session

from ticketer.db.session import get_db
from ticketer.repositories.event_repository import SQLAlchemyEventRepository
from ticketer.repositories.order_repository import SQLAlchemyOrderRepository
from ticketer.repositories.seat_repository import SQLAlchemySeatRepository
from ticketer.repositories.user_repository import SQLAlchemyUserRepository
from ticketer.repositories.venue_repository import SQLAlchemyVenueRepository
from ticketer.services.auth_service import AuthService
from ticketer.services.email_service import RealEmailService
from ticketer.services.event_service import EventService
from ticketer.services.order_service import OrderService
from ticketer.services.payment_gateway import RealPaymentGateway


def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Get user repository."""
    return SQLAlchemyUserRepository(db)


def get_venue_repository(db: Session = Depends(get_db)) -> SQLAlchemyVenueRepository:
    """Get venue repository."""
    return SQLAlchemyVenueRepository(db)


def get_event_repository(db: Session = Depends(get_db)) -> SQLAlchemyEventRepository:
    """Get event repository."""
    return SQLAlchemyEventRepository(db)


def get_seat_repository(db: Session = Depends(get_db)) -> SQLAlchemySeatRepository:
    """Get seat repository."""
    return SQLAlchemySeatRepository(db)


def get_order_repository(db: Session = Depends(get_db)) -> SQLAlchemyOrderRepository:
    """Get order repository."""
    return SQLAlchemyOrderRepository(db)


def get_auth_service(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get auth service."""
    return AuthService(user_repo)


def get_event_service(
    event_repo: SQLAlchemyEventRepository = Depends(get_event_repository),
) -> EventService:
    """Get event service."""
    return EventService(event_repo)


def get_order_service(
    order_repo: SQLAlchemyOrderRepository = Depends(get_order_repository),
    event_repo: SQLAlchemyEventRepository = Depends(get_event_repository),
    seat_repo: SQLAlchemySeatRepository = Depends(get_seat_repository),
) -> OrderService:
    """Get order service with real payment gateway and email service."""
    payment_gateway = RealPaymentGateway(api_key="fake_api_key")
    email_service = RealEmailService(smtp_host="localhost", smtp_port=587)
    return OrderService(
        order_repo=order_repo,
        event_repo=event_repo,
        seat_repo=seat_repo,
        payment_gateway=payment_gateway,
        email_service=email_service,
    )

