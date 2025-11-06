from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


# --- USER MODEL ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="customer")  # "organizer" or "customer"

    events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="customer")


# --- EVENT MODEL ---
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    venue = Column(String)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    organizer = relationship("User", back_populates="events")
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete")


# --- TICKET MODEL ---
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # General, VIP, etc.
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    event = relationship("Event", back_populates="tickets")
    bookings = relationship("Booking", back_populates="ticket")


# --- BOOKING MODEL ---
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    quantity = Column(Integer)
    total_price = Column(Float)
    booking_date = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    ticket = relationship("Ticket", back_populates="bookings")
