import smtplib
from email.message import EmailMessage
from config import ALERT_EMAIL, ALERT_PASSWORD
import os

def send_alert(recipient, subject, message, attachment_path=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL
    msg["To"] = recipient

    if attachment_path:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(ALERT_EMAIL, ALERT_PASSWORD)
        server.send_message(msg)
