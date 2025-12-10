import os
import sys
from dotenv import load_dotenv

# Ensure proper path resolution for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Event, Ticket

load_dotenv()  # Loads GOOGLE_API_KEY from .env


def get_text_from_db():
    """Fetch data from Event and Ticket tables and combine into text docs."""
    db: Session = SessionLocal()
    events = db.query(Event).all()
    tickets = db.query(Ticket).all()
    db.close()

    docs = []

    # Create text chunks from events
    for e in events:
        text = f"""
        Event Title: {e.title}
        Description: {e.description or 'No description available.'}
        Date: {e.date}
        Venue: {e.venue or 'Not specified'}
        Organizer ID: {e.organizer_id}
        """
        docs.append(text)

    # Create text chunks from tickets
    for t in tickets:
        text = f"""
        Ticket Type: {t.type}
        Price: {t.price}
        Quantity: {t.quantity}
        Event ID: {t.event_id}
        """
        docs.append(text)

    return docs


def build_vectorstore():
    """Create embeddings and save them in ChromaDB."""
    print("📦 Fetching data from database...")
    raw_docs = get_text_from_db()

    # Split text into manageable chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,
        chunk_overlap=50,
        length_function=len
    )
    docs = splitter.create_documents(raw_docs)
    print(f"📄 Split into {len(docs)} chunks for embedding.")

    # Initialize embeddings (Gemini)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create Chroma vector store
    persist_directory = os.path.join(os.path.dirname(__file__), "rag_db")
    os.makedirs(persist_directory, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    vectorstore.persist()
    print(f"✅ Vector DB built successfully at: {persist_directory}")




