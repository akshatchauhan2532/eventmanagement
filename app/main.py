from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.database import Base, engine

# Import routers
from app.auth.routes import router as auth_router
from app.events.routes import router as event_router
from app.tickets.routes import router as ticket_router
from app.bookings.routes import router as booking_router

# Import RAG & Auto Refresh
from app.rag.query_rag import get_rag_chain
from app.rag.auto_refresh import start_auto_refresh

import asyncio

app = FastAPI(title="Event Management + Gemini RAG")

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(ticket_router)
app.include_router(booking_router)

# ✅ Start the auto-refresh scheduler (hourly vector DB rebuild)
try:
    start_auto_refresh()
except Exception as e:
    print(f"⚠️ Auto-refresh failed to start: {e}")


@app.get("/")
def root():
    return {"message": "FastAPI + Gemini RAG is connected and running!"}


# ---------------------------------
# 🧠 WebSocket Endpoint for RAG Chat
# ---------------------------------
@app.websocket("/ws/rag")
async def rag_chat(websocket: WebSocket):
    """Real-time Gemini RAG chat via WebSocket."""
    await websocket.accept()
    await websocket.send_text("✅ Connected to Gemini RAG! Ask your question.\n")

    # Load chain once per session
    rag_chain = get_rag_chain()

    try:
        while True:
            # Wait for message
            question = await websocket.receive_text()
            await websocket.send_text(f" You: {question}\n")

            # Stream Gemini response asynchronously
            response_text = ""
            for chunk in rag_chain.stream(question):
                response_text += chunk
                await websocket.send_text(chunk)
                # small sleep to avoid flooding client with too many messages
                await asyncio.sleep(0.01)

            await websocket.send_text(f"\n Final Answer:\n{response_text}\n")

    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected.")
    except Exception as e:
        print(f"❌ Error in RAG WebSocket: {e}")
        await websocket.close()
