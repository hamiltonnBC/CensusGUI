"""
Email service for sending verification emails and password reset links.
"""

from flask import current_app, render_template_string
from flask_mail import Mail, Message
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration."""
    app.config.update(
        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_USERNAME')
    )
    mail.init_app(app)

def send_verification_email(email: str, token: str):
    """Send account verification email."""
    verification_template = """
    <h1>Welcome to CensusConnect!</h1>
    <p>Thank you for registering. Please click the link below to verify your email address:</p>
    <p>
        <a href="{{ url }}">Verify Email Address</a>
    </p>
    <p>If you did not create this account, please ignore this email.</p>
    <p>The verification link will expire in 24 hours.</p>
    """

    verification_url = f"{os.getenv('APP_URL', 'http://127.0.0.1:5000')}/activate/{token}"

    msg = Message(
        subject="Verify Your Email Address",
        recipients=[email],
        html=render_template_string(
            verification_template,
            url=verification_url
        )
    )

    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {str(e)}")
        return False

def send_password_reset_email(email: str, token: str):
    """Send password reset email."""
    reset_template = """
    <h1>Password Reset Request</h1>
    <p>Someone requested a password reset for your account. If this was you, click the link below to reset your password:</p>
    <p>
        <a href="{{ url }}">Reset Password</a>
    </p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>The reset link will expire in 1 hour.</p>
    """

    reset_url = f"{os.getenv('APP_URL', 'http://localhost:5000')}/reset-password/{token}"

    msg = Message(
        subject="Password Reset Request",
        recipients=[email],
        html=render_template_string(
            reset_template,
            url=reset_url
        )
    )

    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False