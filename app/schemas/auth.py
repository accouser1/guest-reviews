"""Authentication schemas"""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    role: str


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    hotel_id: str | None = None
    role: str = "manager"
