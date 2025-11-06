from fastapi import FastAPI
from app.database import Base, engine

from app.auth.routes import router as auth_router
from app.events.routes import router as event_router
from app.tickets.routes import router as ticket_router
from app.bookings.routes import router as booking_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(event_router)
app.include_router(ticket_router)
app.include_router(booking_router)


@app.get("/")
def root():
    return {"message": "FastAPI is connected and running!"}


