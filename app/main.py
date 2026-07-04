# ========================================
# main.py - Application Ka Starting Point
# ========================================
# Yahan FastAPI app create hoti hai
# Saare routers yahan register hain

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # NAYA - CORS ke liye
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles  # NAYA - static files serve karne ke liye

# Models import karo - zaroori hai taake SQLAlchemy tables jaane
from app.models import models  # noqa: F401

# Swagger mein Bearer token field ke liye
security = HTTPBearer()

# ----------------------------------------
# Uploads folder banana (agar na ho to)
# ----------------------------------------
# Yahan product images store hongi
UPLOADS_DIR = Path("uploads/products")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------
# FastAPI App Banao
# ----------------------------------------
app = FastAPI(
    title="MEN SHOES API",
    description="FastAPI + PostgreSQL se bana MEN SHOES E-Commerce Backend",
    version="1.0.0",
)

# ----------------------------------------
# NAYA: CORS Enable Karo
# ----------------------------------------
# Bina is ke frontend (alag origin/port pe chalta hai, e.g. localhost:5173)
# backend ko call nahi kar sakta - browser request block kar deta hai.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Dev ke liye sab origins allow - production mein specific URL daalna
    allow_credentials=False,   # Token Authorization header se jata hai, cookies use nahi hoti
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# NAYA: Static Files Serve Karo
# ----------------------------------------
# Ab /uploads/products/filename.jpg URL pe
# directly images browser mein open ho sakti hain
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ----------------------------------------
# Root Route - Test karne ke liye
# ----------------------------------------
@app.get("/")
def home():
    return {"message": "E-Commerce API chal rahi hai!"}


# ----------------------------------------
# Saare Routers Register Karo
# ----------------------------------------

# Auth - register, login, profile
from app.routers import auth
app.include_router(auth.router)

# Categories - CRUD
from app.routers import categories
app.include_router(categories.router)

# Products - CRUD + Image Upload
from app.routers import products
app.include_router(products.router)

# Cart - add, view, remove
from app.routers import cart
app.include_router(cart.router)

# Orders - create, view
from app.routers import orders
app.include_router(orders.router)
