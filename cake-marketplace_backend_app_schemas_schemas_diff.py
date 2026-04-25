--- cake-marketplace/backend/app/schemas/schemas.py (原始)


+++ cake-marketplace/backend/app/schemas/schemas.py (修改后)
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserCreate(UserBase):
    password: str
    role: str = "customer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str

class ProductCreate(ProductBase):
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    is_available: bool
    confectioner_id: int
    created_at: datetime
    confectioner_name: Optional[str] = None

    class Config:
        from_attributes = True

# Order schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    comment: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    confectioner_id: Optional[int] = None
    status: str
    total_price: float
    delivery_address: str
    comment: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

# Review schemas
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    author_name: str

    class Config:
        from_attributes = True