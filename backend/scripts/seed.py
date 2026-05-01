import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.supabase import supabase
from app.core.security import get_password_hash

def seed_db():
    print("Iniciando Seed de Base de Datos...")

    # 1. Crear campos personalizados iniciales
    fields = [
        {"name": "priority", "label": "Prioridad", "data_type": "select", "options": ["Alta", "Media", "Baja"]},
        {"name": "gift", "label": "¿Es regalo?", "data_type": "boolean"},
    ]
    for f in fields:
        supabase.table("custom_fields").insert(f).execute()
    print("✓ Campos personalizados creados.")

    # 2. Nota: La creación de usuarios en Supabase Auth se recomienda vía consola
    # pero aquí podemos insertar perfiles dummy si ya existen IDs
    print("✓ Seed completado.")

if __name__ == "__main__":
    seed_db()
