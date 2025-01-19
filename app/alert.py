import smtplib
from email.mime.text import MIMEText
from config import ALERT_EMAIL, ALERT_PASSWORD, RECEIVER_EMAIL

def send_alert():
    msg = MIMEText("Alert: Motion detected!")
    msg["Subject"] = "Security Alert"
    msg["From"] = ALERT_EMAIL
    msg["To"] = RECEIVER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(ALERT_EMAIL, ALERT_PASSWORD)
        server.sendmail(ALERT_EMAIL, RECEIVER_EMAIL, msg.as_string())
