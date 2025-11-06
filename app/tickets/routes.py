from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, Event, User
from app.tickets.schemas import TicketCreate, TicketResponse
from app.auth.dependencies import  get_current_user

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# --- CREATE TICKET (Organizer only) --- #
@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add tickets")

    new_ticket = Ticket(**ticket.dict())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


# --- LIST ALL TICKETS FOR A GIVEN EVENT (accessible by anyone logged in) --- #
@router.get("/by-event/{event_id}", response_model=list[TicketResponse])
def get_tickets_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
    return tickets


# --- LIST ALL TICKETS CREATED BY THE ORGANIZER --- #
@router.get("/my", response_model=list[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Organizer can view all tickets they have created for their events."""
    # get all events created by this organizer
    event_ids = [e.id for e in db.query(Event.id).filter(Event.organizer_id == current_user.id)]
    tickets = db.query(Ticket).filter(Ticket.event_id.in_(event_ids)).all()
    return tickets


# --- UPDATE TICKET (Organizer only) --- #
@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")

    for key, value in ticket_data.dict().items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)
    return ticket


# --- DELETE TICKET (Organizer only) --- #
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this ticket")

    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}
