from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, users, deliveries, dashboard
from app.routes.protected_examples import router as examples_router, admin_router

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "**DMS — Delivery Management System API**\n\n"
        "### Autenticación\n"
        "1. Llama `POST /auth/login` para obtener el **access_token**\n"
        "2. Haz clic en **Authorize** (🔒) e ingresa: `Bearer <access_token>`\n"
        "3. El access token expira en 60 min — usa `POST /auth/refresh` para renovar\n"
        "\n### Roles\n"
        "| Rol | Descripción |\n|---|---|\n"
        "| ADMIN | Acceso total |\n"
        "| OPERATOR | Gestión operativa |\n"
        "| DRIVER | Solo sus entregas |\n"
        "| VIEWER | Solo lectura |"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# ── Routers — prefijo /api/v1 ────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=f"{API_PREFIX}/auth",        tags=["Auth"])
app.include_router(users.router,       prefix=f"{API_PREFIX}/users",       tags=["Users"])
app.include_router(deliveries.router,  prefix=f"{API_PREFIX}/deliveries",  tags=["Deliveries"])
app.include_router(custom_fields.router, prefix=f"{API_PREFIX}/custom-fields", tags=["Custom Fields"])
app.include_router(dashboard.router,   prefix=f"{API_PREFIX}/dashboard",   tags=["Dashboard"])
app.include_router(examples_router,    prefix=f"{API_PREFIX}/examples",    tags=["Auth Examples"])
app.include_router(admin_router,       prefix=f"{API_PREFIX}/admin",       tags=["Admin"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
