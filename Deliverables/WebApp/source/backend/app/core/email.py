import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Configuración de fastapi-mail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'email',
)

fast_mail = FastMail(conf)

async def send_verification_email(email: str, token: str, username: str):
    """Envía el email de confirmación usando una plantilla HTML."""
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    # Preparar datos para la plantilla
    template_body = {
        "username": username,
        "verify_url": verify_url
    }
    
    message = MessageSchema(
        subject="¡Bienvenido a Tutunaku! - Confirma tu cuenta",
        recipients=[email],
        template_body=template_body,
        subtype=MessageType.html
    )

    try:
        await fast_mail.send_message(message, template_name="verification.html")
        logger.info("verification_email_sent", email=email, user=username)
    except Exception as e:
        logger.error("failed_to_send_verification_email", email=email, error=str(e))

async def send_password_reset_email(email: str, token: str):
    """Envía el email de recuperación de contraseña usando una plantilla HTML."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    template_body = {
        "reset_url": reset_url,
    }

    message = MessageSchema(
        subject="Recupera tu contraseña de Tutunaku",
        recipients=[email],
        template_body=template_body,
        subtype=MessageType.html
    )

    try:
        await fast_mail.send_message(message, template_name="reset_password.html")
        logger.info("password_reset_email_sent", email=email)
    except Exception as e:
        logger.error("failed_to_send_password_reset_email", email=email, error=str(e))
