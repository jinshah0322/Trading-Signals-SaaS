from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignupRequest(BaseModel):
    """Request model for user signup"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100, description="Password must be at least 6 characters")


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: int
    email: str
    is_paid: bool
    exp: Optional[int] = None