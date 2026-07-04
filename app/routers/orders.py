# ========================================
# routers/orders.py - Order Routes
# ========================================
# Yahan 3 APIs hain (assignment ke mutabiq):
# POST   /orders             → Cart se order banao
# GET    /orders             → Apne sare orders dekho
# GET    /orders/{id}        → Ek order ki detail dekho

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db                              # DB session
from app.models.models import Order, OrderItem, Cart, CartItem, Product, User  # Tables
from app.schemas.order import OrderResponse                           # Schema
from app.core.dependencies import get_current_user                    # Logged in user


# ----------------------------------------
# Router banao
# ----------------------------------------
router = APIRouter(prefix="/orders", tags=["Orders"])


# ========================================
# HELPER - Admin check
# ========================================
def check_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sirf admin yeh kaam kar sakta hai"
        )


# ========================================
# API 1: POST /orders - Cart se naya order banao
# ========================================
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Cart mein jo items hain unka order place karo
    Cart automatically khali ho jayega order ke baad
    """
    # User ka cart dhundho
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    # Cart hai ya nahi
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart khali hai - pehle koi product add karo"
        )

    # Cart mein items hain ya nahi
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart mein koi item nahi hai"
        )

    # ----------------------------------------
    # Total amount calculate karo
    # ----------------------------------------
    total_amount = 0.0

    for cart_item in cart.items:
        # Har item ka product dhundho
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID {cart_item.product_id} nahi mila"
            )

        # Stock check karo
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{product.name} ka stock kam hai - sirf {product.stock_quantity} bache hain"
            )

        # Total mein add karo
        total_amount += product.price * cart_item.quantity

    # ----------------------------------------
    # Order banao
    # ----------------------------------------
    new_order = Order(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),  # 2 decimal places
        status="pending"                       # Default status
    )
    db.add(new_order)
    db.flush()  # ID generate karo commit se pehle

    # ----------------------------------------
    # Order Items banao + Stock update karo
    # ----------------------------------------
    for cart_item in cart.items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()

        # Order item banao
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price  # Us waqt ki price save karo
        )
        db.add(order_item)

        # Stock kam karo
        product.stock_quantity -= cart_item.quantity

    # ----------------------------------------
    # Cart khali karo - order ho gaya
    # ----------------------------------------
    for cart_item in cart.items:
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order)

    return new_order


# ========================================
# API 2: GET /orders - Apne sare orders dekho
# ========================================
@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Apne saare orders dekhne ke liye
    """
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders


# ========================================
# API 2.5 (NAYA): GET /orders/admin/all - Admin sab orders dekhe
# ========================================
@router.get("/admin/all", response_model=list[OrderResponse])
def get_all_orders_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Sab customers ke sare orders dekhne ke liye (sirf admin).
    Admin panel is route ko use karega - GET /orders sirf
    logged-in user ke apne orders deta hai, sab orders nahi.
    """
    check_admin(current_user)
    orders = db.query(Order).all()
    return orders


# ========================================
# API 3: GET /orders/{id} - Ek order ki detail
# ========================================
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Kisi ek order ki poori detail dekhne ke liye
    Sirf apna order dekh sakte ho
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id  # Sirf apna order
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order nahi mila"
        )

    return order
