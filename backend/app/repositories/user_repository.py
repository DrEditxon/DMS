"""
app/repositories/user_repository.py
─────────────────────────────────────
Acceso a datos de usuarios. Sin lógica de negocio.
"""
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.base_repository import BaseRepository
import uuid


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    # ── Búsquedas ──────────────────────────────────────────────
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_active_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        return (
            db.query(User)
            .filter(User.id == user_id, User.is_active == True)
            .first()
        )

    def email_exists(self, db: Session, email: str) -> bool:
        return self.get_by_email(db, email) is not None

    def get_active_drivers(self, db: Session) -> list[User]:
        return (
            db.query(User)
            .filter(User.role == UserRole.DRIVER, User.is_active == True)
            .all()
        )

    # ── Seguridad de sesión ────────────────────────────────────
    def save_refresh_token_hash(
        self, db: Session, user: User, token_hash: str
    ) -> User:
        """Persiste el hash del refresh token para validación futura."""
        user.refresh_token_hash = token_hash
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    def clear_refresh_token(self, db: Session, user: User) -> None:
        """Invalida el refresh token (logout)."""
        user.refresh_token_hash = None
        db.commit()

    def register_failed_login(self, db: Session, user: User) -> User:
        """Incrementa contador de intentos fallidos y bloquea si supera el límite."""
        from datetime import timedelta
        MAX_ATTEMPTS = 5
        LOCK_MINUTES = 15

        user.failed_login_count = (user.failed_login_count or 0) + 1
        if user.failed_login_count >= MAX_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)
        db.commit()
        db.refresh(user)
        return user

    def reset_failed_login(self, db: Session, user: User) -> None:
        """Reinicia contadores tras login exitoso."""
        user.failed_login_count = 0
        user.locked_until = None
        db.commit()

    # ── Estadísticas ───────────────────────────────────────────
    def count_by_role(self, db: Session, role: UserRole) -> int:
        return db.query(User).filter(User.role == role).count()


user_repo = UserRepository()
