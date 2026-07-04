# ========================================
# routers/products.py - Product Routes
# ========================================
# 6 APIs + Search + Image Upload:
# POST   /products                        → Naya product banao (sirf admin)
# GET    /products                        → Sare products dekho
# GET    /products?search=shirt           → Products search karo
# GET    /products/{id}                   → Ek product ki detail dekho
# PUT    /products/{id}                   → Product update karo (sirf admin)
# DELETE /products/{id}                   → Product delete karo (sirf admin)
# POST   /products/{id}/upload-image      → Product ki picture upload karo (sirf admin) ← NAYA

import os
import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.models import Product, Category, User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

# ========================================
# Image Upload ke liye folder banana
# ========================================
# Yeh folder server pe pictures store karega
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Folder na ho to bana do

# Allowed image formats - sirf yeh formats accept honge
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Maximum file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # bytes


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
# API 1: POST /products - Naya product banao
# ========================================
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Naya product banane ke liye (sirf admin):
    {
        "name": "Polo Shirt",
        "description": "Cotton polo shirt",
        "price": 29.99,
        "stock_quantity": 100,
        "category_id": 1
    }

    Product banne ke baad image upload karne ke liye:
    POST /products/{id}/upload-image use karo
    """
    check_admin(current_user)

    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Yeh category exist nahi karti")

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        category_id=product_data.category_id,
        image_url=None  # Pehle None - baad mein upload-image se set hoga
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# ========================================
# API 2: GET /products - Sare products + Search
# ========================================
@router.get("/", response_model=list[ProductResponse])
def get_all_products(
    search: Optional[str] = Query(None, description="Product naam se search karo"),
    db: Session = Depends(get_db)
):
    """
    Sare products dekho - login ki zaroorat nahi

    Search karne ke liye:
    /products?search=shirt
    /products?search=polo
    """
    query = db.query(Product)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_filter) |
            Product.description.ilike(search_filter)
        )

    products = query.all()
    return products


# ========================================
# API 3: GET /products/{id} - Ek product dekho
# ========================================
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Kisi ek product ki detail - login ki zaroorat nahi
    Response mein image_url bhi ayega (agar picture hai to)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila")
    return product


# ========================================
# API 4: PUT /products/{id} - Product update karo
# ========================================
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Product update karne ke liye (sirf admin)
    Sirf wo fields bhejo jo update karni hain
    Note: Image update ke liye /upload-image route use karo
    """
    check_admin(current_user)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila")

    if product_data.category_id is not None:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Yeh category exist nahi karti")

    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.stock_quantity is not None:
        product.stock_quantity = product_data.stock_quantity
    if product_data.category_id is not None:
        product.category_id = product_data.category_id

    db.commit()
    db.refresh(product)
    return product


# ========================================
# API 5: DELETE /products/{id} - Product delete karo
# ========================================
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Product delete karne ke liye (sirf admin)
    Product ke saath uski image file bhi delete ho jayegi
    """
    check_admin(current_user)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila")

    # Agar product ki image hai to woh file bhi delete karo
    if product.image_url:
        old_file = Path(product.image_url.lstrip("/"))
        if old_file.exists():
            old_file.unlink()

    db.delete(product)
    db.commit()
    return {"message": "Product delete ho gaya"}


# ========================================
# API 6 (NAYA): POST /products/{id}/upload-image
# Product ki picture upload karo
# ========================================
@router.post("/{product_id}/upload-image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(..., description="Product ki picture (JPG, PNG, GIF, WEBP)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Product ki picture upload karne ke liye (sirf admin).

    Kaise use karein (Swagger UI / Postman mein):
    - Method: POST
    - URL: /products/{id}/upload-image
    - Body: form-data
    - Key: image  (type: File)
    - Value: apni picture file select karo

    Allowed formats: JPG, JPEG, PNG, GIF, WEBP
    Maximum size: 5 MB

    Success pe response mein image_url aa jata hai jaise:
    "image_url": "/uploads/products/abc123.jpg"

    Yeh URL browser mein directly open hota hai kyunki
    main.py mein /uploads folder ko static serve kiya gaya hai.
    """
    check_admin(current_user)

    # Product exist karta hai?
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila")

    # ----- File Extension Check -----
    original_filename = image.filename or ""
    file_ext = Path(original_filename).suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Yeh format allowed nahi. Sirf yeh formats chalenge: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # ----- File Size Check -----
    # File content read karo
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File bohat bari hai. Maximum 5 MB allowed hai."
        )

    # ----- Purani Image Delete Karo (agar thi) -----
    if product.image_url:
        old_file = Path(product.image_url.lstrip("/"))
        if old_file.exists():
            old_file.unlink()

    # ----- Unique File Name Banao -----
    # UUID use karo taake koi bhi do files same naam se na hon
    unique_name = f"product_{product_id}_{uuid.uuid4().hex}{file_ext}"
    save_path = UPLOAD_DIR / unique_name

    # ----- File Save Karo -----
    with open(save_path, "wb") as f:
        f.write(contents)

    # ----- Database Update Karo -----
    # URL format: /uploads/products/filename.jpg
    # Browser mein directly accessible hoga
    product.image_url = f"/uploads/products/{unique_name}"
    db.commit()
    db.refresh(product)

    return product
