# ========================================
# schemas/user.py - User Schemas
# ========================================
# Yeh schemas define karte hain:
# - Register karte waqt kya data aaye
# - Login karte waqt kya data aaye
# - Response mein kya data bheja jaye

from pydantic import BaseModel, EmailStr  # BaseModel = schema ka base, EmailStr = email validation
from typing import Optional
from datetime import datetime


# ========================================
# REGISTER SCHEMA - Naya user banate waqt
# ========================================
class UserCreate(BaseModel):
    """
    POST /register pe yeh data aana chahiye
    Teeno fields required hain
    """
    full_name: str        # Pura naam
    email: EmailStr       # Valid email (pydantic khud check karega)
    password: str         # Plain password (hum hash karenge)


# ========================================
# LOGIN SCHEMA - Login karte waqt
# ========================================
class UserLogin(BaseModel):
    """
    POST /login pe yeh data aana chahiye
    """
    email: EmailStr       # Email
    password: str         # Password


# ========================================
# RESPONSE SCHEMA - User data wapas bhejte waqt
# ========================================
class UserResponse(BaseModel):
    """
    API response mein user ki yeh info jayegi
    Password kabhi response mein nahi aayega!
    """
    id: int
    full_name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model se directly kaam karega


# ========================================
# TOKEN SCHEMA - Login ke baad JWT token
# ========================================
class Token(BaseModel):
    """
    Login successful hone ke baad yeh response milega
    """
    access_token: str     # JWT token
    token_type: str       # "bearer"


class TokenData(BaseModel):
    """
    JWT token ke andar jo data store hoga
    """
    email: Optional[str] = None
