from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import requests
import os
from models import get_db
from models.whatsapp_session import WhatsAppSession
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

WHATSAPP_SERVICE_URL = os.getenv("WHATSAPP_SERVICE_URL", "http://localhost:3001")

class WhatsAppSessionCreate(BaseModel):
    restaurant_id: str
    phone_number: str

class WhatsAppSessionResponse(BaseModel):
    id: str
    restaurant_id: str
    phone_number: str
    is_connected: bool
    qr_code: Optional[str]

    class Config:
        from_attributes = True

@router.post("/session", response_model=WhatsAppSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_whatsapp_session(
    session_data: WhatsAppSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == session_data.restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Verificar se já existe uma sessão
    existing_session = db.query(WhatsAppSession).filter(
        WhatsAppSession.restaurant_id == session_data.restaurant_id
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp session already exists for this restaurant"
        )
    
    # Criar sessão no serviço WhatsApp
    try:
        response = requests.post(
            f"{WHATSAPP_SERVICE_URL}/session/create",
            json={
                "restaurant_id": session_data.restaurant_id,
                "phone_number": session_data.phone_number
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create WhatsApp session"
            )
        
        whatsapp_data = response.json()
        
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WhatsApp service is unavailable"
        )
    
    # Salvar sessão no banco de dados
    new_session = WhatsAppSession(
        restaurant_id=session_data.restaurant_id,
        phone_number=session_data.phone_number,
        session_id=whatsapp_data.get("session_id"),
        qr_code=whatsapp_data.get("qr_code")
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

@router.get("/session/{restaurant_id}", response_model=WhatsAppSessionResponse)
async def get_whatsapp_session(
    restaurant_id: str,
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
    
    session = db.query(WhatsAppSession).filter(
        WhatsAppSession.restaurant_id == restaurant_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp session not found"
        )
    
    # Verificar status no serviço WhatsApp
    try:
        response = requests.get(
            f"{WHATSAPP_SERVICE_URL}/session/status/{session.session_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            status_data = response.json()
            session.is_connected = status_data.get("is_connected", False)
            session.qr_code = status_data.get("qr_code")
            db.commit()
    except requests.exceptions.RequestException:
        pass
    
    return session

@router.delete("/session/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_whatsapp_session(
    restaurant_id: str,
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
    
    session = db.query(WhatsAppSession).filter(
        WhatsAppSession.restaurant_id == restaurant_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp session not found"
        )
    
    # Deletar sessão no serviço WhatsApp
    try:
        requests.delete(
            f"{WHATSAPP_SERVICE_URL}/session/{session.session_id}",
            timeout=5
        )
    except requests.exceptions.RequestException:
        pass
    
    db.delete(session)
    db.commit()
    
    return None