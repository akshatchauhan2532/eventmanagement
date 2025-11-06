from datetime import timedelta,datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, Booking, User, Event
from app.bookings.schemas import BookingCreate, BookingResponse
from app.auth.dependencies import get_current_user
from datetime import datetime, timedelta, timezone

from app.celery_worker import celery_app
from app.utils.email_utils import send_booking_email, send_event_reminder_email



router = APIRouter(prefix="/bookings", tags=["Bookings"])


# --- BOOK TICKET --- #
@router.post("/", response_model=BookingResponse)
def book_ticket(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Fetch ticket
    ticket = db.query(Ticket).filter(Ticket.id == booking.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # ✅ Fetch related event for title
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # ✅ Check quantity
    if ticket.quantity < booking.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")

    # ✅ Calculate total price
    total_price = ticket.price * booking.quantity

    # ✅ Create booking
    new_booking = Booking(
        customer_id=current_user.id,
        event_id=event.id,
        ticket_id=ticket.id,
        quantity=booking.quantity,
        total_price=total_price,
    )

    # ✅ Update ticket quantity
    ticket.quantity -= booking.quantity
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    db.add(ticket)
    db.commit()

    # ✅ Send confirmation email asynchronously
    send_booking_email.delay(
        current_user.email,
        event.title,        # ✅ use event.title instead of ticket.name
        booking.quantity,
        total_price
    )

    reminder_time = event.date - timedelta(minutes=5)
    current_utc = datetime.now(timezone.utc)

    if reminder_time > current_utc:
        send_event_reminder_email.apply_async(
            args=[
                current_user.email,
                event.title,
                event.date.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                event.venue,
            ],
            eta=reminder_time  # ✅ Celery uses UTC internally
        )

    return new_booking


# --- CANCEL BOOKING --- #
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id, Booking.customer_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Restore tickets
    ticket = db.query(Ticket).filter(Ticket.id == booking.ticket_id).first()
    ticket.quantity += booking.quantity

    db.delete(booking)
    db.commit()

    db.add(ticket)
    db.commit()

    return {"message": "Booking canceled successfully"}


# --- GET ALL BOOKINGS FOR CURRENT USER --- #
@router.get("/", response_model=list[BookingResponse])
def get_user_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = db.query(Booking).filter(Booking.customer_id == current_user.id).all()
    return bookings
