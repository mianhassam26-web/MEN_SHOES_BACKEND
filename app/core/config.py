# ========================================
# config.py - Project Settings
# ========================================
# Yeh file .env se saari settings padhti hai
# Jab bhi koi setting chahiye, yahan se milegi

from pydantic_settings import BaseSettings  # .env file padhne ke liye


class Settings(BaseSettings):
    """
    Yeh class saari project settings store karti hai.
    .env file se automatically values aa jati hain.
    """

    # Database connection string
    DATABASE_URL: str

    # JWT ke liye secret key
    SECRET_KEY: str

    # JWT algorithm (HS256 standard hai)
    ALGORITHM: str = "HS256"

    # Token kitne minutes tak valid rahega
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        # .env file ka naam batao
        env_file = ".env"


# Ek baar settings object banao, poore project mein yahi use hoga
settings = Settings()
