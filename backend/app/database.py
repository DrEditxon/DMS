from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine_args = {} if settings.DATABASE_URL.startswith("sqlite") else {
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para inyectar sesión de BD en cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
