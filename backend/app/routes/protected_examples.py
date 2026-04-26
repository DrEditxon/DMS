"""
app/routes/protected_examples.py
──────────────────────────────────
Ejemplos de uso del sistema de autenticación en rutas protegidas.

Demuestra todos los patrones disponibles:
  1. Ruta pública
  2. Cualquier usuario autenticado
  3. Solo ADMIN
  4. Solo ADMIN u OPERATOR
  5. ADMIN, OPERATOR o DRIVER
  6. Factory require_roles (custom)
  7. Dependencia opcional (semi-pública)
  8. Verificación de propiedad de recurso
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.middleware.auth_middleware import (
    get_current_user,
    get_optional_user,
    require_admin,
    require_operator,
    require_driver,
    require_roles,
)

router = APIRouter(prefix="/examples", tags=["Auth Examples"])


# ── 1. Ruta pública — sin autenticación ──────────────────────────────────────
@router.get("/public", summary="[PÚBLICO] Sin autenticación")
def public_endpoint():
    return {"message": "Accesible sin token"}


# ── 2. Cualquier usuario autenticado ─────────────────────────────────────────
@router.get(
    "/authenticated",
    summary="[AUTH] Cualquier rol",
)
def authenticated_only(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": f"Hola, {current_user.full_name}",
        "role": current_user.role,
        "email": current_user.email,
    }


# ── 3. Solo ADMIN ─────────────────────────────────────────────────────────────
@router.get(
    "/admin-only",
    summary="[ADMIN] Solo administradores",
)
def admin_only(
    admin: User = Depends(require_admin),
):
    return {
        "message": "Panel de administración",
        "admin": admin.full_name,
        "accessible_by": ["ADMIN"],
    }


# ── 4. ADMIN u OPERATOR ───────────────────────────────────────────────────────
@router.get(
    "/operator",
    summary="[ADMIN | OPERATOR] Gestión operativa",
)
def operator_dashboard(
    user: User = Depends(require_operator),
):
    return {
        "message": "Dashboard operativo",
        "user": user.full_name,
        "role": user.role,
        "accessible_by": ["ADMIN", "OPERATOR"],
    }


# ── 5. ADMIN, OPERATOR o DRIVER ───────────────────────────────────────────────
@router.get(
    "/driver",
    summary="[ADMIN | OPERATOR | DRIVER] Acceso de campo",
)
def driver_area(
    user: User = Depends(require_driver),
):
    return {
        "message": "Área de repartidores",
        "accessible_by": ["ADMIN", "OPERATOR", "DRIVER"],
    }


# ── 6. Uso del factory require_roles (roles custom) ───────────────────────────
# Define una dependencia reutilizable para combinaciones específicas
require_reports = require_roles(UserRole.ADMIN, UserRole.OPERATOR)

@router.get(
    "/reports",
    summary="[ADMIN | OPERATOR] Reportes (usando factory)",
)
def reports(
    user: User = Depends(require_reports),
):
    """
    Usa el factory `require_roles()` para crear dependencias personalizadas.
    Equivalente a `require_operator` pero más explícito y reutilizable.
    """
    return {
        "message": "Acceso a reportes",
        "user": user.full_name,
        "pattern": "require_roles(ADMIN, OPERATOR)",
    }


# ── 7. Semi-pública (más datos si está autenticado) ───────────────────────────
@router.get(
    "/semi-public",
    summary="[OPCIONAL] Respuesta enriquecida si autenticado",
)
def semi_public(
    user: User | None = Depends(get_optional_user),
):
    base = {"public_data": "Visible para todos", "deliveries_today": 42}
    if user:
        base["private_data"] = f"Hola {user.full_name}, tu rol es {user.role}"
    return base


# ── 8. Verificación de propiedad de recurso ───────────────────────────────────
@router.get(
    "/deliveries/{delivery_id}",
    summary="[AUTH] Solo el driver asignado o ADMIN/OPERATOR puede ver",
)
def get_delivery_protected(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Patrón de 'ownership check':
    - ADMIN y OPERATOR siempre tienen acceso
    - DRIVER solo ve sus propias entregas
    """
    # En producción aquí harías: delivery = delivery_repo.get(db, delivery_id)
    driver_id_simulado = current_user.id  # Simulación para el ejemplo

    is_privileged = current_user.role in (UserRole.ADMIN, UserRole.OPERATOR)
    is_owner = driver_id_simulado == current_user.id  # Compara con la FK real

    if not is_privileged and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta entrega",
        )

    return {
        "delivery_id": delivery_id,
        "accessed_by": current_user.email,
        "access_type": "privileged" if is_privileged else "owner",
    }


# ── 9. Usar como dependencia a nivel de router completo ───────────────────────
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],   # ← Protege TODAS las rutas del router
)

@admin_router.get("/users/stats", summary="[ADMIN] Estadísticas de usuarios")
def user_stats(db: Session = Depends(get_db)):
    """
    Todas las rutas de `admin_router` requieren rol ADMIN
    sin necesidad de declararlo en cada endpoint.
    """
    return {"pattern": "dependencies en APIRouter", "scope": "todas las rutas del router"}
