"""
app/routes/deliveries.py
─────────────────────────
Router del módulo de entregas — prefijo: /api/v1/deliveries

Endpoints propios:
  POST   /                        Crear entrega               [ADMIN]
  GET    /                        Listar entregas              [ALL]
  GET    /{delivery_id}           Detalle de entrega           [ALL]
  PUT    /{delivery_id}           Actualizar campos            [ADMIN, OPERATOR]
  PATCH  /{delivery_id}/status    Cambiar estado               [ADMIN, OPERATOR, DRIVER]
  DELETE /{delivery_id}           Eliminar (soft delete)       [ADMIN]

Sub-router montado:
  /{delivery_id}/items/*          → delivery_items.router      [ver delivery_items.py]
"""
from typing import Optional
from uuid import UUID

from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.delivery import DeliveryStatus
from app.models.user import User
from app.schemas.delivery import (
    DeliveryCreate, DeliveryFilters, DeliveryPage,
    DeliveryRead, DeliveryStatusUpdate, DeliveryUpdate, DeliveryCompleteRequest,
)
from app.services import delivery_service, export_service
from app.routes.delivery_items import router as items_router

router = APIRouter()

# ── Sub-router de ítems montado como recurso anidado ─────────────────────────
router.include_router(
    items_router,
    prefix="/{delivery_id}/items",
    tags=["Delivery Items"],
)


# ══════════════════════════════════════════════════════════
#  POST / — Crear entrega
# ══════════════════════════════════════════════════════════
@router.post(
    "/",
    response_model=DeliveryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear entrega",
    description=(
        "Crea una nueva entrega con sus ítems y dirección en una sola request.\n\n"
        "**Rol requerido:** `ADMIN`\n\n"
        "La dirección se geocodifica automáticamente via OpenStreetMap/Nominatim.\n"
        "Si se provee `driver_id`, el estado inicial será `ASSIGNED`; "
        "de lo contrario `PENDING`.\n\n"
        "El campo `items` acepta una lista de ítems que se crean junto con la entrega."
    ),
)
async def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await delivery_service.create_delivery(db, payload, current_user)


# ══════════════════════════════════════════════════════════
#  GET / — Listar entregas
# ══════════════════════════════════════════════════════════
@router.get(
    "/",
    response_model=DeliveryPage,
    summary="Listar entregas",
    description=(
        "Listado paginado con filtros avanzados.\n\n"
        "**Visibilidad por rol:**\n"
        "- `ADMIN` / `VIEWER` → todas las entregas\n"
        "- `OPERATOR` → solo las asignadas a él\n"
        "- `DRIVER` → solo las suyas\n\n"
        "**Filtros disponibles:** estado, driver, ciudad, prioridad, "
        "rango de fechas programadas/creadas, búsqueda de texto.\n\n"
        "**Ordenamiento:** `order_by` + `order_dir` (asc/desc)"
    ),
)
def list_deliveries(
    status_filter: Optional[DeliveryStatus] = Query(None, alias="status"),
    driver_id:     Optional[UUID]           = Query(None),
    city:          Optional[str]            = Query(None),
    priority:      Optional[int]            = Query(None, ge=1, le=5),
    scheduled_from:Optional[str]            = Query(None, description="ISO 8601"),
    scheduled_to:  Optional[str]            = Query(None, description="ISO 8601"),
    created_from:  Optional[str]            = Query(None, description="ISO 8601"),
    created_to:    Optional[str]            = Query(None, description="ISO 8601"),
    search:        Optional[str]            = Query(None),
    page:          int                      = Query(1, ge=1),
    size:          int                      = Query(20, ge=1, le=100),
    order_by:      str                      = Query("created_at"),
    order_dir:     str                      = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime

    def _parse(s: Optional[str]):
        return datetime.fromisoformat(s) if s else None

    filters = DeliveryFilters(
        status=status_filter, driver_id=driver_id, city=city,
        priority=priority,
        scheduled_from=_parse(scheduled_from), scheduled_to=_parse(scheduled_to),
        created_from=_parse(created_from),     created_to=_parse(created_to),
        search=search, page=page, size=size,
        order_by=order_by, order_dir=order_dir,
    )
    return delivery_service.list_deliveries(db, filters, current_user)


# ══════════════════════════════════════════════════════════
#  GET /{delivery_id} — Detalle
# ══════════════════════════════════════════════════════════
@router.get(
    "/{delivery_id}",
    response_model=DeliveryRead,
    summary="Detalle de entrega",
    description="Retorna la entrega completa con ítems, dirección y repartidor.",
)
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.get_delivery(db, delivery_id, current_user)


# ══════════════════════════════════════════════════════════
#  PUT /{delivery_id} — Actualizar campos
# ══════════════════════════════════════════════════════════
@router.put(
    "/{delivery_id}",
    response_model=DeliveryRead,
    summary="Actualizar entrega",
    description=(
        "Actualiza campos editables de la entrega (no el estado).\n\n"
        "**Rol requerido:** `ADMIN` o `OPERATOR`\n\n"
        "Solo `ADMIN` puede cambiar el campo `driver_id`.\n"
        "No se puede editar una entrega en estado final."
    ),
)
def update_delivery(
    delivery_id: UUID,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.update_delivery(db, delivery_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  PATCH /{delivery_id}/status — Cambiar estado
# ══════════════════════════════════════════════════════════
@router.patch(
    "/{delivery_id}/status",
    response_model=DeliveryRead,
    summary="Cambiar estado de entrega",
    description=(
        "**Máquina de estados:**\n\n"
        "```\nPENDING → ASSIGNED → IN_PROGRESS → DELIVERED\n"
        "                           └──────────────→ FAILED\n"
        "PENDING / ASSIGNED → CANCELLED\n```\n\n"
        "**Permisos:** ADMIN/OPERATOR → cualquier transición. "
        "DRIVER → solo `IN_PROGRESS → DELIVERED/FAILED`.\n\n"
        "`failure_reason` es obligatorio cuando `status = FAILED`."
    ),
)
def change_status(
    delivery_id: UUID,
    payload: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.change_status(db, delivery_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  POST /{delivery_id}/complete — Finalizar con firma
# ══════════════════════════════════════════════════════════
@router.post(
    "/{delivery_id}/complete",
    response_model=DeliveryRead,
    summary="Finalizar entrega con firma",
    description=(
        "Registra la firma del receptor y la ubicación GPS para marcar la entrega como DELIVERED.\n\n"
        "**Rol requerido:** `ADMIN`, `OPERATOR` o `DRIVER` (asignado)."
    ),
)
def complete_delivery(
    delivery_id: UUID,
    payload: DeliveryCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.complete_delivery(db, delivery_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  EXPORT — Reportes
# ══════════════════════════════════════════════════════════
@router.get("/export/excel", summary="Exportar entregas a Excel")
def export_excel(
    filters: DeliveryFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    output = export_service.generate_excel_report(db, filters)
    filename = f"entregas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/pdf", summary="Exportar entregas a PDF")
def export_pdf(
    filters: DeliveryFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    pdf_bytes = export_service.generate_pdf_report(db, filters)
    filename = f"reporte_entregas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ══════════════════════════════════════════════════════════
#  DELETE /{delivery_id} — Soft delete
# ══════════════════════════════════════════════════════════
@router.delete(
    "/{delivery_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar entrega",
    description=(
        "Soft delete (`is_deleted=True`).\n\n"
        "**Rol requerido:** `ADMIN`\n\n"
        "No se puede eliminar una entrega `DELIVERED`."
    ),
)
def delete_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.delete_delivery(db, delivery_id, current_user)
