"""
app/middleware/auth_middleware.py
──────────────────────────────────
Dependencias de FastAPI para protección de rutas y validación de roles.

Uso en rutas:
    # Cualquier usuario autenticado
    current_user: User = Depends(get_current_user)

    # Solo ADMIN
    user: User = Depends(require_admin)

    # Solo ADMIN u OPERATOR
    user: User = Depends(require_operator)

    # Múltiples roles (uso avanzado)
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR))
"""
import uuid
from functools import lru_cache
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repo
from app.utils.security import decode_token

# ── Esquema Bearer (extrae el token del header Authorization) ─────────────────
bearer_scheme = HTTPBearer(
    scheme_name="JWT",
    description="Token JWT de acceso. Formato: `Bearer <token>`",
    auto_error=True,
)


# ─────────────────────────────────────────────
#  DEPENDENCIA BASE: Extraer usuario del JWT
# ─────────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extrae y valida el JWT del header Authorization.
    Verifica: firma, expiración, tipo ('access'), usuario activo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(credentials.credentials)

    if not payload:
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un access token, no un refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = user_repo.get_active_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ─────────────────────────────────────────────
#  FACTORY: require_roles (genérico y reutilizable)
# ─────────────────────────────────────────────
def require_roles(*roles: UserRole) -> Callable:
    """
    Factory que devuelve una dependencia para cualquier conjunto de roles.

    Ejemplo:
        require_admin_or_operator = require_roles(UserRole.ADMIN, UserRole.OPERATOR)

        @router.get("/", dependencies=[Depends(require_admin_or_operator)])
        def endpoint(): ...
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            role_names = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso restringido. Roles permitidos: {role_names}",
            )
        return current_user
    return _check


# ─────────────────────────────────────────────
#  DEPENDENCIAS PREDEFINIDAS (shortcuts)
# ─────────────────────────────────────────────

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Solo ADMIN puede acceder."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido: se requiere rol ADMIN",
        )
    return current_user


def require_operator(current_user: User = Depends(get_current_user)) -> User:
    """ADMIN u OPERATOR pueden acceder."""
    if current_user.role not in (UserRole.ADMIN, UserRole.OPERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido: se requiere rol ADMIN u OPERATOR",
        )
    return current_user


def require_driver(current_user: User = Depends(get_current_user)) -> User:
    """ADMIN, OPERATOR o DRIVER pueden acceder."""
    if current_user.role not in (UserRole.ADMIN, UserRole.OPERATOR, UserRole.DRIVER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido: se requiere rol DRIVER o superior",
        )
    return current_user


# ─────────────────────────────────────────────
#  DEPENDENCIA OPCIONAL (rutas semi-públicas)
# ─────────────────────────────────────────────
def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> User | None:
    """
    Intenta autenticar pero no falla si no hay token.
    Útil para endpoints que devuelven más datos a usuarios autenticados.
    """
    if not credentials:
        return None
    try:
        return get_current_user(credentials=credentials, db=db)
    except HTTPException:
        return None
