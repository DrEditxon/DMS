"""
app/services/auth_service.py
─────────────────────────────
Lógica de negocio de autenticación.
Responsabilidades:
  - Registro con validaciones de dominio
  - Login con bloqueo por intentos fallidos
  - Emisión y rotación de tokens JWT
  - Logout (invalidación de refresh token)
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse,
    TokenResponse, RefreshRequest, AuthUserRead,
)
from app.repositories.user_repository import user_repo
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, hash_refresh_token, verify_refresh_token_hash,
)


# ─────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────
def register(db: Session, payload: RegisterRequest) -> User:
    """
    Crea un nuevo usuario tras validar:
    - Email único
    - Contraseña con fortaleza validada por Pydantic
    """
    if user_repo.email_exists(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El email '{payload.email}' ya está registrado",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email.lower().strip(),
        phone=payload.phone,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )
    return user_repo.create(db, user)


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def login(db: Session, payload: LoginRequest) -> LoginResponse:
    """
    Autentica al usuario y emite access + refresh tokens.
    Implementa:
      - Bloqueo temporal por intentos fallidos
      - Refresh token rotation (hash guardado en BD)
      - Respuesta unificada con datos del usuario
    """
    user = user_repo.get_by_email(db, payload.email.lower().strip())

    # ── Validaciones ──────────────────────────
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Cuenta bloqueada temporalmente
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta bloqueada. Intenta nuevamente en {remaining} minutos",
        )

    # Contraseña incorrecta
    if not verify_password(payload.password, user.password_hash):
        user_repo.register_failed_login(db, user)
        remaining_attempts = max(0, 5 - (user.failed_login_count or 0))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciales inválidas. Intentos restantes: {remaining_attempts}",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacta al administrador",
        )

    # ── Emisión de tokens ─────────────────────
    token_data = {"sub": str(user.id), "role": user.role.value, "email": user.email}
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Guardar hash del refresh token y actualizar last_login_at
    user_repo.reset_failed_login(db, user)
    user_repo.save_refresh_token_hash(db, user, hash_refresh_token(refresh_token))

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
    )
    return LoginResponse(tokens=tokens, user=AuthUserRead.model_validate(user))


# ─────────────────────────────────────────────
#  REFRESH TOKEN
# ─────────────────────────────────────────────
def refresh_tokens(db: Session, payload: RefreshRequest) -> TokenResponse:
    """
    Rota el par de tokens de forma segura:
    1. Valida el JWT del refresh token
    2. Verifica que el hash coincide con el guardado en BD
       (detecta reuso de refresh tokens robados)
    3. Emite un nuevo par access + refresh
    4. Invalida el token anterior (rotación)
    """
    # 1. Decodificar JWT
    token_payload = decode_token(payload.refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    # 2. Buscar usuario
    import uuid as uuid_lib
    user = user_repo.get_active_by_id(db, uuid_lib.UUID(token_payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    # 3. Validar que el token no fue ya usado (rotación)
    if not user.refresh_token_hash or not verify_refresh_token_hash(
        payload.refresh_token, user.refresh_token_hash
    ):
        # Posible robo de token: invalidar todo
        user_repo.clear_refresh_token(db, user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido. Inicia sesión nuevamente",
        )

    # 4. Emitir nuevos tokens
    token_data = {"sub": str(user.id), "role": user.role.value, "email": user.email}
    new_access  = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    # Rotar: guardar nuevo hash, invalidar el anterior
    user_repo.save_refresh_token_hash(db, user, hash_refresh_token(new_refresh))

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
    )


# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
def logout(db: Session, user: User) -> dict:
    """Invalida el refresh token del usuario (logout seguro)."""
    user_repo.clear_refresh_token(db, user)
    return {"message": "Sesión cerrada correctamente"}
