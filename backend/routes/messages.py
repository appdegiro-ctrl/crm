from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import get_db
from models.message import Message
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])

class MessageResponse(BaseModel):
    id: str
    whatsapp_message_id: Optional[str]
    from_number: str
    to_number: str
    content: str
    message_type: str
    media_url: Optional[str]
    is_from_me: bool
    status: str
    restaurant_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    restaurant_id: str
    to_number: str
    content: str
    message_type: str = "text"

@router.get("/restaurant/{restaurant_id}", response_model=List[MessageResponse])
async def get_messages_by_restaurant(
    restaurant_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    messages = db.query(Message).filter(
        Message.restaurant_id == restaurant_id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return messages

@router.get("/conversation/{restaurant_id}/{phone_number}", response_model=List[MessageResponse])
async def get_conversation(
    restaurant_id: str,
    phone_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    messages = db.query(Message).filter(
        Message.restaurant_id == restaurant_id,
        ((Message.from_number == phone_number) | (Message.to_number == phone_number))
    ).order_by(Message.created_at.asc()).all()
    
    return messages

@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == message_data.restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Aqui você chamaria o serviço WhatsApp para enviar a mensagem
    # Por enquanto, apenas salvaremos no banco de dados
    
    new_message = Message(
        from_number=restaurant.phone or "restaurant",
        to_number=message_data.to_number,
        content=message_data.content,
        message_type=message_data.message_type,
        is_from_me=True,
        restaurant_id=message_data.restaurant_id
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return {"success": True, "message_id": new_message.id}