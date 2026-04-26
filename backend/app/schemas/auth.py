"""
app/schemas/auth.py
────────────────────
Schemas Pydantic para autenticación: entrada, salida y tokens.
"""
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.user import UserRole


# ─────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    """Payload para crear una nueva cuenta."""
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: UserRole = UserRole.DRIVER

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    """Payload para iniciar sesión."""
    email: EmailStr
    password: str


# ─────────────────────────────────────────────
#  TOKENS
# ─────────────────────────────────────────────
class TokenResponse(BaseModel):
    """Respuesta al login o refresh exitoso."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int           # segundos de vida del access token
    role: UserRole


class RefreshRequest(BaseModel):
    """Payload para renovar el access token."""
    refresh_token: str


# ─────────────────────────────────────────────
#  PAYLOAD INTERNO DEL JWT
# ─────────────────────────────────────────────
class TokenPayload(BaseModel):
    """Estructura del payload decodificado del JWT."""
    sub: str               # user_id (UUID como string)
    role: UserRole
    email: str
    type: str              # "access" | "refresh"
    exp: datetime
    iat: datetime


# ─────────────────────────────────────────────
#  RESPUESTA DE USUARIO AUTENTICADO
# ─────────────────────────────────────────────
class AuthUserRead(BaseModel):
    """Info del usuario devuelta tras autenticarse."""
    id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str]
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Respuesta completa al login: tokens + datos del usuario."""
    tokens: TokenResponse
    user: AuthUserRead
