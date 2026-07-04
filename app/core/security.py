# ========================================
# core/security.py - Security Functions
# ========================================

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ========================================
# PASSWORD HASHING SETUP
# ========================================
# bcrypt use kar rahe hain password hash karne ke liye
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Plain password ko hash karo
    bcrypt 72 bytes se zyada accept nahi karta
    isliye pehle truncate karo
    """
    # bcrypt ki limit 72 bytes hai - encode karke trim karo
    password_bytes = password.encode("utf-8")[:72]
    password_trimmed = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password_trimmed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Login pe password check karo
    Same trimming apply karo verify karte waqt bhi
    """
    # Same truncation login pe bhi karni hai
    password_bytes = plain_password.encode("utf-8")[:72]
    password_trimmed = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(password_trimmed, hashed_password)


# ========================================
# JWT TOKEN FUNCTIONS
# ========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT token banao login ke baad
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Token verify karo - sahi hai ya nahi
    Returns: email ya None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
