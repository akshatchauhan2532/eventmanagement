# app/rag/auto_refresh.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.rag.setup_rag import build_vectorstore

def start_auto_refresh():
    """Runs vectorstore rebuild every hour in background."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(build_vectorstore, "interval", hours=1)
    scheduler.start()
    print("⏰ Auto-refresh started (rebuilds every 1 hour).")
