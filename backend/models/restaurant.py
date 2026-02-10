from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import uuid

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    owner = relationship("User", back_populates="restaurants")
    leads = relationship("Lead", back_populates="restaurant")
    messages = relationship("Message", back_populates="restaurant")
    campaigns = relationship("Campaign", back_populates="restaurant")
    products = relationship("Product", back_populates="restaurant")
    whatsapp_session = relationship("WhatsAppSession", back_populates="restaurant", uselist=False)