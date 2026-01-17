from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr


class UserCreate(UserBase):
    """Model for creating a user"""
    password: str = Field(..., min_length=6, max_length=100)


class UserInDB(UserBase):
    """User model as stored in database"""
    id: int
    password_hash: str
    is_paid: bool = False
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User model for API responses (without sensitive data)"""
    id: int
    is_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True