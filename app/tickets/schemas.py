# app/tickets/schemas.py
from pydantic import BaseModel

class TicketCreate(BaseModel):
    type: str  # 'VIP', 'General', etc.
    price: float
    quantity: int
    event_id: int

class TicketResponse(TicketCreate):
    id: int
    event_id: int

    class Config:
        orm_mode = True
