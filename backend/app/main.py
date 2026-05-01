import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from app.api.v1 import auth, deliveries, delivery_items, proofs, custom_fields, stats, notifications, users
from app.core.config import settings
from app.core.websocket import manager

# Configuración de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("DMS_API")

app = FastAPI(title=settings.PROJECT_NAME)

# Manejo Global de Errores
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error inesperado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Ha ocurrido un error interno en el servidor."},
    )

# Incluir Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(deliveries.router, prefix=f"{settings.API_V1_STR}/deliveries", tags=["deliveries"])
app.include_router(delivery_items.router, prefix=f"{settings.API_V1_STR}/deliveries", tags=["items"])
app.include_router(proofs.router, prefix=f"{settings.API_V1_STR}/deliveries", tags=["proofs"])
app.include_router(custom_fields.router, prefix=f"{settings.API_V1_STR}/custom-fields", tags=["custom-fields"])
app.include_router(stats.router, prefix=f"{settings.API_V1_STR}/stats", tags=["stats"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {"message": "DMS API is running"}
