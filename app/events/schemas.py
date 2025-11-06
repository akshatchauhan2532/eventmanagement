# app/events/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    venue: Optional[str] = None


# --- CREATE EVENT --- #
class EventCreate(EventBase):
    pass


# --- EVENT RESPONSE --- #
class EventResponse(EventBase):
    id: int
    organizer_id: int

    class Config:
        from_attributes = True
