from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import get_db
from models.product import Product
from models.restaurant import Restaurant
from models.user import User
from middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/products", tags=["Products"])

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None
    restaurant_id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    category: Optional[str]
    is_available: bool
    restaurant_id: str

    class Config:
        from_attributes = True

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verificar se o restaurante pertence ao usuário
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == product_data.restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    new_product = Product(**product_data.dict())
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/restaurant/{restaurant_id}", response_model=List[ProductResponse])
async def get_products_by_restaurant(
    restaurant_id: str,
    category: Optional[str] = None,
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
    
    query = db.query(Product).filter(Product.restaurant_id == restaurant_id)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).join(Restaurant).filter(
        Product.id == product_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).join(Restaurant).filter(
        Product.id == product_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).join(Restaurant).filter(
        Product.id == product_id,
        Restaurant.owner_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return None