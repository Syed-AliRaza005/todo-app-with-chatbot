from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


# ====================
# User Schemas
# ====================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response with JWT token"""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID


# ====================
# Token Schemas
# ====================

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id as string
    exp: datetime
    iat: datetime


class RevokedTokenCreate(BaseModel):
    """Schema for creating a revoked token record"""
    token_jti: str
    user_id: UUID
    expires_at: datetime
