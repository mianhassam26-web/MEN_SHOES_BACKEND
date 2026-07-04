# ========================================
# database.py - Database Connection Setup
# ========================================
# Yeh file PostgreSQL se connection banati hai
# SQLAlchemy ORM use kar raha hai

from sqlalchemy import create_engine          # Database engine banane ke liye
from sqlalchemy.ext.declarative import declarative_base  # Models ka base class
from sqlalchemy.orm import sessionmaker       # Database session ke liye

from app.core.config import settings          # .env se DATABASE_URL lene ke liye


# ----------------------------------------
# Step 1: Engine banao (Database se connection)
# ----------------------------------------
# Engine = Database ka darwaza, isse hi sab kuch hoga
engine = create_engine(settings.DATABASE_URL)


# ----------------------------------------
# Step 2: Session Factory banao
# ----------------------------------------
# Session = Ek conversation with database
# autocommit=False matlab hum khud commit karenge
# autoflush=False matlab hum khud flush karenge
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ----------------------------------------
# Step 3: Base Class banao
# ----------------------------------------
# Saare models (tables) is Base se inherit karenge
Base = declarative_base()


# ----------------------------------------
# Step 4: Database Session Dependency
# ----------------------------------------
def get_db():
    """
    Yeh function har API request pe ek naya database session deta hai.
    Request khatam hone pe session automatically band ho jata hai.
    
    Use: FastAPI ke routers mein Depends(get_db) likhenge
    """
    db = SessionLocal()  # Naya session kholo
    try:
        yield db          # Router ko session do
    finally:
        db.close()        # Kaam khatam, session band karo
