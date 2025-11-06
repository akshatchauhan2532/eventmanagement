from pydantic import BaseModel
from datetime import datetime

class BookingBase(BaseModel):
    ticket_id: int
    quantity: int

class BookingCreate(BookingBase):
    pass

class BookingResponse(BaseModel):
    id: int
    ticket_id: int
    customer_id: int
    quantity: int
    booking_date: datetime

    class Config:
        orm_mode = True