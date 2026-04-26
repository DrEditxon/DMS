from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import user_repo
from app.utils.security import hash_password
import uuid


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return user_repo.get_all(db, skip=skip, limit=limit)


def get_by_id(db: Session, user_id: uuid.UUID) -> User:
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def create(db: Session, payload: UserCreate) -> User:
    if user_repo.email_exists(db, payload.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )
    return user_repo.create(db, user)


def update(db: Session, user_id: uuid.UUID, payload: UserUpdate) -> User:
    user = get_by_id(db, user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    return user_repo.update(db, user)


def deactivate(db: Session, user_id: uuid.UUID) -> User:
    user = get_by_id(db, user_id)
    user.is_active = False
    return user_repo.update(db, user)
