"""
app/utils/security.py
─────────────────────
Utilidades de seguridad: bcrypt, JWT access + refresh tokens.
"""
import hashlib
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings

# ── Contexto bcrypt ───────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────────────────────
#  Contraseñas
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Genera hash bcrypt de la contraseña."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica contraseña contra su hash bcrypt."""
    return pwd_context.verify(plain, hashed)


# ─────────────────────────────────────────────
#  JWT — Access Token (vida corta)
# ─────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT de acceso con expiración corta.
    Payload esperado: {"sub": str(user_id), "role": role_value, "email": email}
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access", "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ─────────────────────────────────────────────
#  JWT — Refresh Token (vida larga)
# ─────────────────────────────────────────────
def create_refresh_token(data: dict) -> str:
    """
    Crea un JWT de refresco con vida larga.
    Solo contiene sub + exp para minimizar superficie de ataque.
    """
    to_encode = {"sub": data["sub"]}
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ─────────────────────────────────────────────
#  JWT — Decodificación
# ─────────────────────────────────────────────
def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica y verifica un JWT.
    Retorna el payload o None si es inválido/expirado.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ─────────────────────────────────────────────
#  Refresh Token — Hash para almacenamiento
# ─────────────────────────────────────────────
def hash_refresh_token(token: str) -> str:
    """
    Genera SHA-256 del refresh token para almacenar en BD.
    Nunca se guarda el token completo, solo su huella digital.
    Permite invalidación por rotación (refresh token rotation).
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token_hash(token: str, stored_hash: str) -> bool:
    """Verifica que el refresh token coincide con el hash almacenado."""
    return hashlib.sha256(token.encode()).hexdigest() == stored_hash
