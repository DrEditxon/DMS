from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from app.core.config import settings
from app.core import security
from app.schemas.auth import TokenPayload, UserResponse, UserRole

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    token: str = Depends(reusable_oauth2)
) -> UserResponse:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Aquí normalmente buscarías en la DB. 
    # Por ahora simulamos un usuario extraído del token o DB mock.
    # user = user_repository.get(id=token_data.sub)
    
    # Mock de usuario para el ejemplo
    return UserResponse(
        id=token_data.sub,
        email="user@example.com",
        full_name="User Mock",
        role=UserRole.ADMIN # Esto debería venir de la DB
    )

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserResponse = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return user
