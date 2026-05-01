from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "DMS API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_ME" # En producción usar env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase (Opcional si usas el cliente directo)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
