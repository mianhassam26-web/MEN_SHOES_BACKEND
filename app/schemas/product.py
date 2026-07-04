# ========================================
# schemas/product.py - Product Schemas
# ========================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ========================================
# CREATE SCHEMA - Naya product banate waqt
# ========================================
class ProductCreate(BaseModel):
    """
    POST /products pe yeh data aana chahiye (JSON body)
    Note: Image alag se POST /products/{id}/upload-image se upload hogi
    """
    name: str                           # Product ka naam (required)
    description: Optional[str] = None  # Detail (optional)
    price: float                        # Price (required)
    stock_quantity: int = 0             # Stock (default 0)
    category_id: Optional[int] = None  # Konsi category (optional)


# ========================================
# UPDATE SCHEMA - Product update karte waqt
# ========================================
class ProductUpdate(BaseModel):
    """
    PUT /products/{id} pe yeh data aana chahiye
    Sab optional hain - sirf jo update karna ho wo bhejo
    """
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None


# ========================================
# RESPONSE SCHEMA - Product data wapas bhejte waqt
# ========================================
class ProductResponse(BaseModel):
    """
    API response mein product ki yeh info jayegi
    image_url bhi shamil hai - agar picture nahi to null ayega
    """
    id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category_id: Optional[int]
    image_url: Optional[str]   # NAYA - Product ki picture ka URL
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model se kaam karega
