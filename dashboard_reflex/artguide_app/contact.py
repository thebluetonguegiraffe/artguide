"""Contact-form email delivery via Gmail SMTP."""
import os
import smtplib
from email.mime.text import MIMEText


def send_contact_email(name: str, sender_email: str, message: str) -> bool:
    """Send a contact-form submission to FEEDBACK_RECIPIENT. Returns success."""
    user = os.environ.get("GMAIL_USER")
    pwd = os.environ.get("GMAIL_PWD")
    to = os.environ.get("FEEDBACK_RECIPIENT")
    if not (user and pwd and to):
        return False

    body = f"From: {name} <{sender_email}>\n\n{message}"
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"ArtGuide — new contact from {name}"
    msg["From"] = user
    msg["To"] = to
    msg["Reply-To"] = sender_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(user, pwd)
            server.sendmail(user, [to], msg.as_string())
        return True
    except Exception:
        return False
