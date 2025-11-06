from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, User
from app.events.schemas import EventCreate, EventResponse
from app.auth.dependencies import  get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


# --- CREATE EVENT (Organizer only) --- #
@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_event = Event(**event.dict(), organizer_id=current_user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# --- GET ALL EVENTS (any logged-in user) --- #
@router.get("/", response_model=list[EventResponse])
def get_all_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.query(Event).all()
    return events


# --- GET EVENTS CREATED BY ORGANIZER --- #
@router.get("/my-events", response_model=list[EventResponse])
def get_my_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Organizer can view only their own created events."""
    events = db.query(Event).filter(Event.organizer_id == current_user.id).all()
    return events


# --- UPDATE EVENT (Organizer only) --- #
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_event = db.query(Event).filter(
        Event.id == event_id, Event.organizer_id == current_user.id
    ).first()

    if not existing_event:
        raise HTTPException(status_code=404, detail="Event not found or not authorized")

    for key, value in event.dict().items():
        setattr(existing_event, key, value)

    db.commit()
    db.refresh(existing_event)
    return existing_event


# --- DELETE EVENT (Organizer only) --- #
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(
        Event.id == event_id, Event.organizer_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not authorized")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}



@router.get("/with-tickets")
def get_events_with_tickets(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    if not events:
        raise HTTPException(status_code=404, detail="No events found")

    result = []
    for event in events:
        event_data = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "venue": event.venue,
            "organizer_id": event.organizer_id,
            "tickets": [
                {
                    "id": ticket.id,
                    "type": ticket.type,
                    "price": ticket.price,
                    "quantity": ticket.quantity
                }
                for ticket in event.tickets
            ],
        }
        result.append(event_data)

    return result
