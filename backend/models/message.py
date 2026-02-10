from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import uuid

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    whatsapp_message_id = Column(String)  # ID da mensagem no WhatsApp
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, audio, video, document
    media_url = Column(String)
    is_from_me = Column(Boolean, default=False)
    status = Column(String, default="sent")  # sent, delivered, read, failed
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    restaurant = relationship("Restaurant", back_populates="messages")