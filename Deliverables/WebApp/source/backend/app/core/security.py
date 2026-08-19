"""
Tutunaku - Módulo de seguridad y autenticación
JWT, hashing de contraseñas, verificación de tokens
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = structlog.get_logger()

# ============================================
# HASHING DE CONTRASEÑAS (bcrypt)
# ============================================
def hash_password(password: str) -> str:
    """Genera hash seguro de contraseña con bcrypt."""
    salt = bcrypt.gensalt()
    # bcrypt requires bytes, then we store as string
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra su hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


# ============================================
# JWT TOKENS
# ============================================
security = HTTPBearer()


def create_access_token(
    subject: str | Any,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Crea un JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """Crea un JWT refresh token de larga duración."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(16),  # ID único para invalidar tokens
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica y valida un JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning("invalid_token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def generate_verification_token() -> str:
    """Genera token aleatorio para verificación de email."""
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """Genera token para recuperación de contraseña."""
    return secrets.token_urlsafe(32)


# ============================================
# DEPENDENCIAS FASTAPI
# ============================================
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extrae y valida el user_id del token JWT."""
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
        )
    return user_id


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extrae el rol del usuario del token JWT."""
    payload = decode_token(credentials.credentials)
    return payload.get("role", "user")


def require_role(*roles: str):
    """Dependency factory para verificar roles."""
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        """Verifica si el usuario tiene uno de los roles requeridos."""
        payload = decode_token(credentials.credentials)
        user_role = payload.get("role", "user")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(roles)}",
            )
        return payload
    return role_checker


# Shortcuts de dependencias comunes
require_admin = require_role("admin")
require_user = require_role("user", "admin")
