# ========================================
# schemas/cart.py - Cart Schemas
# ========================================

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.product import ProductResponse  # NAYA - product ki detail cart mein bhejne ke liye


# ========================================
# ADD TO CART SCHEMA - Cart mein product add karte waqt
# ========================================
class CartItemAdd(BaseModel):
    """
    POST /cart/add pe yeh data aana chahiye
    """
    product_id: int     # Konsa product add karna hai
    quantity: int = 1   # Kitna quantity (default 1)


# ========================================
# CART ITEM RESPONSE - Ek cart item ki info
# ========================================
class CartItemResponse(BaseModel):
    """
    Cart ke andar ek product ki info
    NAYA: 'product' field add ki gayi hai taake frontend ko
    product ka naam, price, image_url bhi mil sake bina
    alag se GET /products/{id} call kiye.
    """
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None  # NAYA

    class Config:
        from_attributes = True


# ========================================
# CART RESPONSE - Poore cart ki info
# ========================================
class CartResponse(BaseModel):
    """
    GET /cart pe poora cart milega
    """
    id: int
    user_id: int
    created_at: datetime
    items: list[CartItemResponse] = []  # Cart mein saare products

    class Config:
        from_attributes = True
