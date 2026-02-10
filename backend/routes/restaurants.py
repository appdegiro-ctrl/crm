from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import get_db
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])

class RestaurantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class RestaurantResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    is_active: bool
    owner_id: str

    class Config:
        from_attributes = True

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    new_restaurant = Restaurant(
        **restaurant_data.dict(),
        owner_id=current_user.id
    )
    
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    
    return new_restaurant

@router.get("/", response_model=List[RestaurantResponse])
async def get_restaurants(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    restaurants = db.query(Restaurant).filter(
        Restaurant.owner_id == current_user.id
    ).all()
    
    return restaurants

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return restaurant

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: str,
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    for key, value in restaurant_data.dict().items():
        setattr(restaurant, key, value)
    
    db.commit()
    db.refresh(restaurant)
    
    return restaurant

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    db.delete(restaurant)
    db.commit()
    
    return None