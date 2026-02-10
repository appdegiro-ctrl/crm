from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import get_db
from models.campaign import Campaign, CampaignStatus
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    message_template: str
    restaurant_id: str
    scheduled_at: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    message_template: Optional[str] = None
    status: Optional[CampaignStatus] = None
    scheduled_at: Optional[datetime] = None

class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    message_template: str
    status: CampaignStatus
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    target_count: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    restaurant_id: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == campaign_data.restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    new_campaign = Campaign(**campaign_data.dict())
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    return new_campaign

@router.get("/restaurant/{restaurant_id}", response_model=List[CampaignResponse])
async def get_campaigns_by_restaurant(
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
    
    campaigns = db.query(Campaign).filter(
        Campaign.restaurant_id == restaurant_id
    ).order_by(Campaign.created_at.desc()).all()
    
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).join(Restaurant).filter(
        Campaign.id == campaign_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).join(Restaurant).filter(
        Campaign.id == campaign_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    for key, value in campaign_data.dict(exclude_unset=True).items():
        setattr(campaign, key, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).join(Restaurant).filter(
        Campaign.id == campaign_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()
    
    return None

@router.post("/{campaign_id}/start", response_model=CampaignResponse)
async def start_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).join(Restaurant).filter(
        Campaign.id == campaign_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.status != CampaignStatus.DRAFT and campaign.status != CampaignStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign already started or completed"
        )
    
    campaign.status = CampaignStatus.RUNNING
    campaign.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(campaign)
    
    # Aqui você iniciaria o processo de envio das mensagens
    # Por enquanto, apenas alteramos o status
    
    return campaign