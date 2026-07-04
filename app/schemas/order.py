# ========================================
# schemas/order.py - Order Schemas
# ========================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schemas.product import ProductResponse  # NAYA - product ki detail order mein bhejne ke liye


# ========================================
# ORDER ITEM RESPONSE
# ========================================
class OrderItemResponse(BaseModel):
    """
    Order ke andar ek product ki info
    Assignment: id, order_id, product_id, quantity, price
    NAYA: 'product' field add ki gayi hai taake frontend ko
    product ka naam aur image_url bhi mil sake.
    """
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    product: Optional[ProductResponse] = None  # NAYA

    class Config:
        from_attributes = True


# ========================================
# ORDER RESPONSE
# ========================================
class OrderResponse(BaseModel):
    """
    Order ka poora response
    Assignment: id, user_id, total_amount, status, created_at
    """
    id: int
    user_id: int
    total_amount: float
    status: str           # String rakha - pending, processing, shipped, delivered, cancelled
    created_at: datetime
    order_items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True
