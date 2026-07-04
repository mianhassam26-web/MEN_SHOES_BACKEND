# ========================================
# routers/cart.py - Cart Routes
# ========================================
# Assignment ke mutabiq 3 APIs:
# POST   /cart/add           → Cart mein product add karo
# GET    /cart               → Apna cart dekho
# DELETE /cart/item/{id}     → Cart se item hatao

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Cart, CartItem, Product, User
from app.schemas.cart import CartItemAdd, CartResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# ========================================
# HELPER - User ka cart dhundho ya banao
# ========================================
def get_or_create_cart(user_id: int, db: Session) -> Cart:
    """
    Agar user ka cart pehle se hai toh wahi do
    Nahi hai toh naya banao
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


# ========================================
# API 1: POST /cart/add - Cart mein product add karo
# ========================================
@router.post("/add", response_model=CartResponse)
def add_to_cart(
    item_data: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cart mein product add karne ke liye:
    {
        "product_id": 1,
        "quantity": 2
    }
    """
    # Product exist karta hai?
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila")

    # Stock check karo
    if product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock mein sirf {product.stock_quantity} items hain"
        )

    # Cart lo ya banao
    cart = get_or_create_cart(current_user.id, db)

    # Product pehle se cart mein hai?
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
        # Quantity add karo
        existing_item.quantity += item_data.quantity
    else:
        # Naya item add karo
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)
    return cart


# ========================================
# API 2: GET /cart - Apna cart dekho
# ========================================
@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apna cart dekhne ke liye
    Cart nahi hai toh khali cart return karega
    """
    # Cart dhundho - nahi hai toh banao (khali wala)
    cart = get_or_create_cart(current_user.id, db)
    return cart


# ========================================
# API 3: DELETE /cart/item/{id} - Cart se item hatao
# ========================================
@router.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cart se koi item hatane ke liye
    item_id = cart_items table ka id
    """
    # User ka cart dhundho
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart nahi mila")

    # Sirf apne cart ka item delete ho sake
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Yeh item tumhare cart mein nahi hai")

    db.delete(cart_item)
    db.commit()

    return {"message": "Item cart se hata diya gaya"}
