"""
Tutunaku - Rutas de Autenticación
Registro, login, refresh tokens, verificación, recuperación de contraseña con CAPTCHA
"""
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import Response
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.captcha import create_captcha, verify_captcha
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_password_reset_token,
    generate_verification_token,
    get_current_user_id,
    hash_password,
    verify_password,
)
from app.core.email import send_verification_email, send_password_reset_email
from app.models.mysql_models import (
    EmailVerification,
    PasswordReset,
    RefreshToken,
    User,
)
from app.schemas.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    StandardResponse,
    TokenResponse,
)

router = APIRouter()
logger = structlog.get_logger()


# ============================================
# POST /auth/register
# ============================================
@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Registra un nuevo usuario."""
    # Verificar email único
    existing = await db.execute(
        select(User).where(User.email == data.email.lower())
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Este email ya está registrado")

    # Verificar username único
    existing_username = await db.execute(
        select(User).where(User.username == data.username.lower())
    )
    if existing_username.scalar_one_or_none():
        raise ConflictError("Este nombre de usuario ya está en uso")

    # Crear usuario
    user = User(
        email=data.email.lower(),
        username=data.username.lower(),
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        hearts=5,
        xp_total=0,
        level=1,
        current_streak=0,
    )
    db.add(user)
    await db.flush()  # Para obtener el ID

    # Crear token de verificación de email
    verification_token = generate_verification_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    verification = EmailVerification(
        user_id=user.id,
        token=verification_token,
        expires_at=expires,
    )
    db.add(verification)
    await db.commit()

    # Enviar email de verificación en background
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        token=verification_token,
        username=user.username,
    )

    logger.info("user_registered", user_id=user.id, email=user.email)

    try:
        from app.sockets.server import emit_admin_new_user
        await emit_admin_new_user({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as exc:  # noqa: BLE001 - el registro nunca debe fallar por esto
        logger.warning("admin_new_user_emit_failed", error=str(exc))

    return StandardResponse(
        message="Registro exitoso. Revisa tu email para verificar tu cuenta.",
        data={"user_id": user.id},
    )


# ============================================
# POST /auth/login
# ============================================
@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Inicia sesión y retorna tokens JWT."""
    result = await db.execute(
        select(User).where(User.email == data.email.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Email o contraseña incorrectos")

    if not user.is_active:
        raise UnauthorizedError("Tu cuenta está desactivada")

    if not user.is_email_verified:
        raise UnauthorizedError("Por favor, verifica tu correo electrónico para poder iniciar sesión.")

    # Crear tokens
    access_token = create_access_token(user.id, role=user.role.value)
    refresh_token_str = create_refresh_token(user.id)

    # Guardar refresh token en BD
    expires = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=expires,
    )
    db.add(refresh_token)

    # Actualizar última actividad
    user.last_activity_date = datetime.now(timezone.utc)
    await db.commit()

    logger.info("user_logged_in", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ============================================
# POST /auth/refresh
# ============================================
@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Renueva el access token usando el refresh token."""
    # Decodificar refresh token
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Token de tipo inválido")

    # Verificar que el token existe en BD y no está revocado
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.token == data.refresh_token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise UnauthorizedError("Refresh token inválido o expirado")

    # Obtener usuario
    user_result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("Usuario no encontrado o desactivado")

    # Revocar token antiguo (rotación)
    token_record.is_revoked = True

    # Crear nuevos tokens
    new_access = create_access_token(user.id, role=user.role.value)
    new_refresh = create_refresh_token(user.id)

    expires = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    new_token_record = RefreshToken(
        user_id=user.id,
        token=new_refresh,
        expires_at=expires,
    )
    db.add(new_token_record)
    await db.commit()

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ============================================
# POST /auth/verify-email
# ============================================
@router.post("/verify-email", response_model=StandardResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verifica el email del usuario."""
    result = await db.execute(
        select(EmailVerification).where(
            and_(
                EmailVerification.token == token,
                EmailVerification.is_used == False,
                EmailVerification.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise UnauthorizedError("Token de verificación inválido o expirado")

    # Marcar como usado y verificar usuario
    verification.is_used = True
    user_result = await db.execute(select(User).where(User.id == verification.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_email_verified = True
    await db.commit()

    return StandardResponse(message="Email verificado exitosamente")


# ============================================
# GET /auth/captcha — Genera un nuevo CAPTCHA
# ============================================
@router.get("/captcha")
async def get_captcha():
    """Genera una nueva imagen CAPTCHA y retorna captcha_id + imagen base64."""
    import base64
    captcha_id, image_bytes = create_captcha()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return {
        "captcha_id": captcha_id,
        "image": f"data:image/png;base64,{image_b64}",
    }


# ============================================
# POST /auth/forgot-password — Con verificación CAPTCHA
# Envía un enlace de recuperación por email (el usuario elige su propia
# contraseña nueva en /reset-password, en vez de recibir una generada)
# ============================================
@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Envía un email con un enlace para restablecer la contraseña, tras validar el CAPTCHA."""
    # Verificar CAPTCHA
    if not data.captcha_id or not data.captcha_answer:
        raise UnauthorizedError("Debes completar el CAPTCHA")

    if not verify_captcha(data.captcha_id, data.captcha_answer):
        raise UnauthorizedError("El CAPTCHA es incorrecto o ha expirado. Intenta de nuevo.")

    # Mensaje de respuesta idéntico exista o no la cuenta: evita que alguien
    # use este endpoint para enumerar qué emails están registrados.
    generic_message = (
        "Si existe una cuenta con ese email, te enviamos un enlace para "
        "restablecer tu contraseña."
    )

    result = await db.execute(select(User).where(User.email == data.email.lower()))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        reset_token = generate_password_reset_token()
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.add(PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires,
        ))
        await db.commit()

        background_tasks.add_task(
            send_password_reset_email,
            email=user.email,
            token=reset_token,
        )

        logger.info("password_reset_requested", user_id=user.id, email=user.email)

    return StandardResponse(message=generic_message)


# ============================================
# POST /auth/reset-password
# ============================================
@router.post("/reset-password", response_model=StandardResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Restablece la contraseña con token válido."""
    result = await db.execute(
        select(PasswordReset).where(
            and_(
                PasswordReset.token == data.token,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    reset = result.scalar_one_or_none()
    if not reset:
        raise UnauthorizedError("Token de recuperación inválido o expirado")

    reset.is_used = True
    user_result = await db.execute(select(User).where(User.id == reset.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.hashed_password = hash_password(data.new_password)
    await db.commit()

    return StandardResponse(message="Contraseña restablecida exitosamente")


# ============================================
# POST /auth/change-password — Cambio de contraseña (autenticado)
# ============================================
@router.post("/change-password", response_model=StandardResponse)
async def change_password(
    data: ChangePasswordRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Permite al usuario cambiar su contraseña actual."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("Usuario no encontrado")

    # Verificar contraseña actual
    if not verify_password(data.current_password, user.hashed_password):
        raise UnauthorizedError("La contraseña actual es incorrecta")

    # Actualizar contraseña
    user.hashed_password = hash_password(data.new_password)
    await db.commit()

    logger.info("user_password_changed", user_id=user.id)

    return StandardResponse(message="Contraseña actualizada exitosamente")


# ============================================
# POST /auth/logout
# ============================================
@router.post("/logout", response_model=StandardResponse)
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Invalida el refresh token (logout)."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == data.refresh_token)
    )
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.is_revoked = True
        await db.commit()

    return StandardResponse(message="Sesión cerrada exitosamente")
