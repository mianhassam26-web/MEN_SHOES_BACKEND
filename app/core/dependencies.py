# ========================================
# core/dependencies.py - Shared Dependencies
# ========================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import verify_token
from app.models.models import User

# ----------------------------------------
# HTTPBearer - Swagger mein seedha "Value" field milegi
# Token format: sirf token daalo, "Bearer" apne aap add hoga
# ----------------------------------------
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Har protected route mein yeh function chalega
    Token verify karega aur user return karega
    """
    token = credentials.credentials  # Sirf token nikalo

    email = verify_token(token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token galat hai ya expire ho gaya",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User nahi mila",
        )

    return user
