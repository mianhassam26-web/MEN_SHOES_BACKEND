# ========================================
# routers/auth.py - Authentication Routes
# ========================================
# Yahan 3 APIs hain:
# POST /register  → Naya account banao
# POST /login     → Login karo, token lo
# GET  /profile   → Apni profile dekho (login zaroori)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db              # DB session
from app.models.models import User                    # User table
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token  # Schemas
from app.core.security import hash_password, verify_password, create_access_token  # Security functions
from app.core.dependencies import get_current_user    # Logged in user


# ----------------------------------------
# Router banao
# ----------------------------------------
# prefix nahi diya - assignment ke mutabiq routes /register, /login, /profile hain (bina /auth ke)
router = APIRouter(tags=["Authentication"])


# ========================================
# API 1: REGISTER - Naya user banao
# ========================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Naya account banane ke liye:
    {
        "full_name": "Ali Ahmed",
        "email": "ali@gmail.com",
        "password": "mypassword123"
    }
    """

    # Check karo yeh email pehle se registered toh nahi
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yeh email pehle se registered hai"
        )

    # Password hash karo (plain text kabhi save mat karo)
    hashed = hash_password(user_data.password)

    # Naya user object banao
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed,  # Hash save karo, plain password nahi
        role="user"            # Default role
    )

    # Database mein save karo
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # ID aur created_at lene ke liye

    return new_user


# ========================================
# API 2: LOGIN - Token lo
# ========================================
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login karne ke liye:
    {
        "email": "ali@gmail.com",
        "password": "mypassword123"
    }
    
    Response mein JWT token milega
    """

    # Email se user dhundho
    user = db.query(User).filter(User.email == user_data.email).first()

    # User nahi mila ya password galat hai
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ya password galat hai"
        )

    # JWT token banao - email token mein store hogi
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ========================================
# API 3: PROFILE - Apni info dekho
# ========================================
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Apni profile dekhne ke liye (login zaroori hai)
    Header mein token bhejo:
    Authorization: Bearer <token>
    """
    return current_user
