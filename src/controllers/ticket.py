from sqlalchemy.orm import Session
from src.schemas.ticket import TicketCreate, TicketOrder
from src.models.ticket import Ticket
from src.models.user import User
from src.schemas.ticket_status import TicketStatus


def create_ticket(db: Session, ticket: TicketCreate, user: User):
    ticket = Ticket(
        **ticket.model_dump(),
        status=TicketStatus.NEW,
        user_id=user.id,
        username=user.username,
    )
    db.add(ticket)
    db.commit()
    return ticket


def get_user_tickets(db: Session, user: User):
    query = db.query(Ticket).filter(Ticket.user_id == str(user.id)).all()
    return query


def get_all_tickets(
    db: Session,
    user_id: str | None = None,
    status: TicketStatus | None = None,
    skip: int = 0,
    limit: int = 10,
    order: TicketOrder = TicketOrder.LAT,
):
    query = db.query(Ticket)
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    if status:
        query = query.filter(Ticket.status == status)
    if order.name == "OLD":
        query = query.order_by(Ticket.created_at.asc())
    else:
        query = query.order_by(Ticket.created_at.desc())
    tickets = query.offset(skip).limit(limit).all()
    return tickets
