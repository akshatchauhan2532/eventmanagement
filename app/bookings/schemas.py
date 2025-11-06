# app/bookings/schemas.py
from pydantic import BaseModel
from datetime import datetime

class BookingCreate(BaseModel):
    ticket_id: int
    quantity: int

class BookingResponse(BookingCreate):
    id: int
    total_price: float
    booking_date: datetime

    class Config:
        orm_mode = True
