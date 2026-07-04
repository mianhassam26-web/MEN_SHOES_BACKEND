# ========================================
# routers/categories.py - Category Routes
# ========================================
# Yahan 4 APIs hain (assignment ke mutabiq):
# POST   /categories          → Naya category banao (sirf admin)
# GET    /categories          → Sari categories dekho
# PUT    /categories/{id}     → Category update karo (sirf admin)
# DELETE /categories/{id}     → Category delete karo (sirf admin)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db                          # DB session
from app.models.models import Category, User                      # DB tables
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse  # Schemas
from app.core.dependencies import get_current_user                # Logged in user


# ----------------------------------------
# Router banao
# ----------------------------------------
router = APIRouter(prefix="/categories", tags=["Categories"])


# ========================================
# HELPER FUNCTION - Admin check karo
# ========================================
def check_admin(current_user: User):
    """
    Sirf admin yeh kaam kar sakta hai
    Agar admin nahi hai toh 403 error dega
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sirf admin yeh kaam kar sakta hai"
        )


# ========================================
# API 1: POST /categories - Naya category banao
# ========================================
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Naya category banane ke liye (sirf admin):
    {
        "name": "Electronics",
        "description": "Electronic products"
    }
    """
    # Admin check karo
    check_admin(current_user)

    # Duplicate name check karo
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Is naam ki category pehle se mojood hai"
        )

    # Naya category banao
    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# ========================================
# API 2: GET /categories - Sari categories dekho
# ========================================
@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """
    Sari categories ki list - koi bhi dekh sakta hai (login ki zaroorat nahi)
    """
    categories = db.query(Category).all()
    return categories


# ========================================
# API 3: PUT /categories/{id} - Category update karo
# ========================================
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Category update karne ke liye (sirf admin):
    {
        "name": "New Name",
        "description": "New description"
    }
    """
    # Admin check karo
    check_admin(current_user)

    # Category dhundho
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category nahi mili"
        )

    # Sirf wo fields update karo jo bheje gaye hain
    if category_data.name is not None:
        category.name = category_data.name
    if category_data.description is not None:
        category.description = category_data.description

    db.commit()
    db.refresh(category)

    return category


# ========================================
# API 4: DELETE /categories/{id} - Category delete karo
# ========================================
@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Login zaroori
):
    """
    Category delete karne ke liye (sirf admin)
    """
    # Admin check karo
    check_admin(current_user)

    # Category dhundho
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category nahi mili"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category delete ho gayi"}
