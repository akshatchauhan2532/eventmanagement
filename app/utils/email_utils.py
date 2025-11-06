from app.celery_worker import celery_app
from celery import shared_task
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")



@shared_task
def send_booking_email(to_email: str, event_title: str, quantity: int, total_price: float):
    subject = f"Booking Confirmation for {event_title}"
    body = f"""
    Hi there,

    Your booking for '{event_title}' has been confirmed.
    Quantity: {quantity}
    Total Price: ₹{total_price}

    Thank you for booking with us!
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"
    

@shared_task
def send_event_reminder_email(to_email: str, event_title: str, event_time: str, venue: str):
    subject = f"Reminder: {event_title} starts soon!"
    body = f"""
    Hi there,

    This is a friendly reminder that the event '{event_title}' will start at {event_time}.

    Venue: {venue}

    See you there!
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        return "Reminder email sent successfully!"
    except Exception as e:
        return f"Failed to send reminder email: {e}"
