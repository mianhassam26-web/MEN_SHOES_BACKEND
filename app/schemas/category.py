# ========================================
# schemas/category.py - Category Schemas
# ========================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ========================================
# CREATE SCHEMA - Naya category banate waqt
# ========================================
class CategoryCreate(BaseModel):
    """
    POST /categories pe yeh data aana chahiye
    """
    name: str                        # Category ka naam (required)
    description: Optional[str] = None  # Description (optional)


# ========================================
# UPDATE SCHEMA - Category update karte waqt
# ========================================
class CategoryUpdate(BaseModel):
    """
    PUT /categories/{id} pe yeh data aana chahiye
    Dono optional hain - sirf jo update karna ho wo bhejo
    """
    name: Optional[str] = None
    description: Optional[str] = None


# ========================================
# RESPONSE SCHEMA - Category data wapas bhejte waqt
# ========================================
class CategoryResponse(BaseModel):
    """
    API response mein category ki yeh info jayegi
    """
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model se kaam karega
