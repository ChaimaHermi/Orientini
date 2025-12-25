import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_reset_email(to_email: str, reset_link: str):
    if not settings.MAIL or not settings.MAIL_PASSWORD:
        return  # mode dev

    msg = MIMEText(f"Reset your password: {reset_link}")
    msg["Subject"] = "Password reset"
    msg["From"] = settings.MAIL
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(settings.MAIL, settings.MAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
