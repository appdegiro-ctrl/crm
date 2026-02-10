from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import uuid

class WhatsAppSession(Base):
    __tablename__ = "whatsapp_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False, unique=True)
    phone_number = Column(String, nullable=False)
    session_id = Column(String, unique=True)  # ID da sessão no serviço WhatsApp
    qr_code = Column(Text)  # QR Code para conexão
    is_connected = Column(Boolean, default=False)
    last_connected_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    restaurant = relationship("Restaurant", back_populates="whatsapp_session")