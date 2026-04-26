import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import engine, Base
# Import models to register them with Base
from app.models.user import User
from app.models.address import Address
from app.models.delivery import Delivery
from app.models.delivery_item import DeliveryItem
from app.models.delivery_proof import DeliveryProof
from app.models.audit_log import AuditLog
from app.models.custom_field import CustomField

print("Creating tables in SQLite...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
