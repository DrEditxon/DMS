from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.schemas.auth import Token, UserCreate, UserResponse, UserRole
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate):
    # 1. Verificar si el usuario ya existe en Supabase/DB
    # 2. Hashear password
    hashed_password = security.get_password_hash(user_in.password)
    
    # 3. Guardar en DB (Mock)
    return UserResponse(
        id="new-uuid",
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Buscar usuario por email
    # 2. Verificar password
    # if not security.verify_password(form_data.password, hashed_db_password):
    #    raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # 3. Generar tokens
    return Token(
        access_token=security.create_access_token(subject="user-id-here"),
        refresh_token=security.create_refresh_token(subject="user-id-here"),
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    # Validar refresh token y emitir nuevo access token
    return Token(
        access_token=security.create_access_token(subject="user-id-here"),
        refresh_token=refresh_token,
        token_type="bearer"
    )

# --- EJEMPLO DE RUTA PROTEGIDA ---

@router.get("/admin-only", dependencies=[Depends(deps.RoleChecker([UserRole.ADMIN]))])
def read_admin_data():
    return {"message": "Solo los administradores ven esto"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(deps.get_current_user)):
    return current_user
