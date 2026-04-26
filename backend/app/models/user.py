import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN    = "ADMIN"     # Acceso total al sistema
    OPERATOR = "OPERATOR"  # Gestión operativa (sin admin de usuarios)
    DRIVER   = "DRIVER"    # Solo sus propias entregas
    VIEWER   = "VIEWER"    # Solo lectura


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name     = Column(String(150), nullable=False)
    email         = Column(String(255), unique=True, index=True, nullable=False)
    phone         = Column(String(30), nullable=True)
    password_hash      = Column(String(255), nullable=False)
    role               = Column(SAEnum(UserRole), default=UserRole.DRIVER, nullable=False)
    is_active          = Column(Boolean, default=True)
    # Seguridad de sesión
    refresh_token_hash = Column(String(255), nullable=True)  # Hash del último refresh token
    last_login_at      = Column(DateTime, nullable=True)
    failed_login_count = Column(Integer, default=0)          # Bloqueo por intentos fallidos
    locked_until       = Column(DateTime, nullable=True)     # Bloqueo temporal
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    deliveries    = relationship("Delivery", back_populates="driver", foreign_keys="Delivery.driver_id")
    audit_logs    = relationship("AuditLog", back_populates="actor")

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"
