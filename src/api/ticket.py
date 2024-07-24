from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.utils.database import get_db
from src.utils.auth import RoleChecker
from src.models.ticket import Ticket
from src.models.user import User
from src.schemas.api_response import APIResponse
from src.schemas.ticket import TicketCreate, TicketDetails
from src.schemas.ticket_misc import TicketStatus, TicketOrder
from src.controllers.ticket import TicketController

tickets = APIRouter(prefix="/tickets", tags=["Tickets"])


@tickets.get("/", response_model=list[TicketDetails])
async def ticket_get_my(
    ticket_id: int | None = None,
    status: TicketStatus | None = None,
    skip: int = 0,
    limit: int = 10,
    order: TicketOrder = TicketOrder.LAT,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(allowed_roles=["Customer"])),
):
    controller = TicketController(db=db)
    return controller.get_tickets(
        user_id=user.id,
        ticket_id=ticket_id,
        status=status,
        skip=skip,
        limit=limit,
        order=order,
    )


@tickets.get("/all/", response_model=list[TicketDetails])
async def ticket_get_all(
    ticket_id: int | None = None,
    user_id: str | None = None,
    status: TicketStatus | None = None,
    skip: int = 0,
    limit: int = 10,
    order: TicketOrder = TicketOrder.LAT,
    db: Session = Depends(get_db),
    _: User = Depends(RoleChecker(allowed_roles=["Pharmacist"])),
):
    controller = TicketController(db=db)
    return controller.get_tickets(
        user_id=user_id,
        ticket_id=ticket_id,
        status=status,
        skip=skip,
        limit=limit,
        order=order,
    )


@tickets.post("/", response_model=TicketDetails)
async def ticket_create(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(allowed_roles=["Customer"])),
):
    controller = TicketController(db=db)
    return controller.create_ticket(ticket=ticket, user=user)


@tickets.put("/", response_model=TicketDetails)
async def ticket_status_update(
    ticket_id: int,
    status: TicketStatus,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(allowed_roles=["Pharmacist"])),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise Exception(detail="Ticket not found.")

    controller = TicketController(db=db)
    return controller.update_ticket_status(status=status, ticket=ticket, user=user)


@tickets.get("/history/", response_model=APIResponse)
async def ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(allowed_roles=["Customer", "Pharmacist"])),
):
    response = APIResponse()

    try:
        # Get ticket by Id
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id)
        # Check if user is not a Pharmacist
        if "Pharmacist" not in user.roles:
            # Restrict to tickets created by the user
            ticket = ticket.filter(Ticket.user_id == str(user.id))
        ticket = ticket.first()

        # Raise an exception if ticket not found
        if not ticket:
            raise Exception("Ticket not found.")

        controller = TicketController(db=db)
        response.data = jsonable_encoder(controller.get_ticket_history(ticket=ticket))
        response.status = "success"

    except Exception as e:
        response.status = "error"
        response.message = e.args[0]

    return response
