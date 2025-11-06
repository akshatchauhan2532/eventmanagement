# app/bookings/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, Booking, User, Event
from app.bookings.schemas import BookingCreate, BookingResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# --- BOOK TICKET (Customer only) --- #
@router.post("/", response_model=BookingResponse)
def book_ticket(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == booking.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.quantity < booking.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")

    total_price = ticket.price * booking.quantity
    new_booking = Booking(
        customer_id=current_user.id,
        event_id=ticket.event_id,
        ticket_id=ticket.id,
        quantity=booking.quantity,
        total_price=total_price,
    )

    # Update ticket quantity after booking
    ticket.quantity -= booking.quantity
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    db.add(ticket)  # Update ticket quantity in DB
    db.commit()

    return new_booking


# --- CANCEL BOOKING (Customer only) --- #
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.customer_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Restore the ticket quantity when booking is canceled
    ticket = db.query(Ticket).filter(Ticket.id == booking.ticket_id).first()
    ticket.quantity += booking.quantity

    db.delete(booking)
    db.commit()

    db.add(ticket)  # Update ticket quantity in DB
    db.commit()

    return {"message": "Booking canceled successfully"}
