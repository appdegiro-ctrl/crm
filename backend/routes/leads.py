from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import get_db
from models.lead import Lead, LeadStatus
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/leads", tags=["Leads"])

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    restaurant_id: str

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str]
    status: LeadStatus
    notes: Optional[str]
    whatsapp_id: Optional[str]
    restaurant_id: str

    class Config:
        from_attributes = True

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == lead_data.restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    new_lead = Lead(**lead_data.dict())
    
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    
    return new_lead

@router.get("/restaurant/{restaurant_id}", response_model=List[LeadResponse])
async def get_leads_by_restaurant(
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
    
    leads = db.query(Lead).filter(Lead.restaurant_id == restaurant_id).all()
    
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).join(Restaurant).filter(
        Lead.id == lead_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).join(Restaurant).filter(
        Lead.id == lead_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    for key, value in lead_data.dict(exclude_unset=True).items():
        setattr(lead, key, value)
    
    db.commit()
    db.refresh(lead)
    
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).join(Restaurant).filter(
        Lead.id == lead_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    db.delete(lead)
    db.commit()
    
    return None