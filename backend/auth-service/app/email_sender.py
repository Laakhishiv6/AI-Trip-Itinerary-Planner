import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings


def send_otp_email(to_email: str, otp: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Voyonata Verification Code"
    msg["From"] = settings.smtp_user
    msg["To"] = to_email

    body = f"""
    <html><body>
    <h2>Email Verification</h2>
    <p>Your one-time verification code is:</p>
    <h1 style="letter-spacing:6px; font-size:36px;">{otp}</h1>
    <p>This code expires in {settings.otp_expire_minutes} minutes. Do not share it with anyone.</p>
    </body></html>
    """
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, to_email, msg.as_string())
