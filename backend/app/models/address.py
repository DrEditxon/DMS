import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    street      = Column(String(255), nullable=False)
    city        = Column(String(100), nullable=False)
    state       = Column(String(100), nullable=True)
    country     = Column(String(100), default="Colombia")
    postal_code = Column(String(20), nullable=True)
    lat         = Column(Float, nullable=True)
    lng         = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Address {self.street}, {self.city}>"
