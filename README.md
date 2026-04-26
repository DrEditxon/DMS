# 🚚 DMS — Delivery Management System

Sistema de gestión de entregas escalable construido con **FastAPI + Next.js + PostgreSQL + Leaflet/OSM**.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14 (App Router) + TailwindCSS |
| Backend | FastAPI + SQLAlchemy |
| Base de datos | PostgreSQL 15 + PostGIS |
| Mapas | Leaflet + OpenStreetMap + Nominatim |
| Auth | JWT (access + refresh tokens) + bcrypt |
| Estado | SWR (remoto) + Zustand (global) |

## Inicio rápido

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores
```

### 2. Levantar con Docker Compose

```bash
docker-compose up --build
```

### 3. Acceder

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

## Desarrollo local (sin Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
# Configura DATABASE_URL en .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Estructura

```
dms/
├── backend/         # FastAPI (routes → services → repos → models)
├── frontend/        # Next.js (módulos: auth, dashboard, deliveries, users)
├── docker-compose.yml
└── .env.example
```

## Roles

| Rol | Permisos |
|---|---|
| ADMIN | CRUD completo + dashboard |
| DRIVER | Ver y actualizar sus propias entregas |
| VIEWER | Solo lectura |

## Estados de entrega

```
PENDING → ASSIGNED → IN_TRANSIT → DELIVERED
                              └→ FAILED
```
