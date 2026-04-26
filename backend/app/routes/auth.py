"""
app/routes/auth.py
───────────────────
Endpoints de autenticación:
  POST /auth/register  — Registro de nuevo usuario
  POST /auth/login     — Login, devuelve access + refresh token
  POST /auth/refresh   — Rota el par de tokens
  POST /auth/logout    — Invalida el refresh token
  GET  /auth/me        — Perfil del usuario autenticado
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse,
    TokenResponse, RefreshRequest, AuthUserRead,
)
from app.schemas.user import UserRead
from app.services import auth_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta. La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    **Reglas:**
    - Email único en el sistema
    - Contraseña: mín. 8 chars, 1 mayúscula, 1 número
    - El campo `role` solo puede ser asignado por un ADMIN en producción
    """
    return auth_service.register(db, payload)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesión",
    description="Autentica al usuario y devuelve access token (vida corta) + refresh token (vida larga).",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    **Respuesta incluye:**
    - `access_token`: JWT de corta duración (default: 60 min)
    - `refresh_token`: JWT de larga duración (default: 7 días)
    - `expires_in`: vida del access token en segundos
    - `user`: datos básicos del usuario autenticado

    **Seguridad:**
    - Bloqueo temporal tras 5 intentos fallidos (15 minutos)
    - El refresh token se hashea (SHA-256) y se almacena en BD
    """
    return auth_service.login(db, payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
    description="Intercambia un refresh token válido por un nuevo par de tokens (rotación).",
)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    **Refresh Token Rotation:**
    - El refresh token anterior queda invalidado inmediatamente
    - Si se detecta reuso de un token ya rotado → sesión invalidada (posible robo)
    - Enviar el nuevo `refresh_token` en las siguientes llamadas
    """
    return auth_service.refresh_tokens(db, payload)


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Invalida el refresh token del usuario. El access token expirará por su cuenta.",
)
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Nota:** El access token sigue siendo válido hasta su expiración natural.
    Para revocación inmediata en producción, usa una blocklist (Redis).
    """
    return auth_service.logout(db, current_user)


@router.get(
    "/me",
    response_model=AuthUserRead,
    summary="Perfil del usuario autenticado",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Devuelve los datos del usuario dueño del token."""
    return current_user
