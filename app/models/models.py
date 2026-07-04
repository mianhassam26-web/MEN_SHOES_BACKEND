# ========================================
# models.py - Database Tables (SQLAlchemy)
# ========================================
# Yahan saari database tables define hain
# Har class = ek table in PostgreSQL
# Assignment ke database design ke mutabiq banaya hai

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship  # Tables ke beech relation ke liye
from sqlalchemy.sql import func          # Server-side timestamp ke liye
import enum                              # Status ke options ke liye

from app.database.database import Base  # Base class import karo


# ========================================
# ENUM - Order Status ke Options
# ========================================
class OrderStatus(str, enum.Enum):
    """
    Order ke possible statuses
    str inherit kiya taake JSON mein string aye
    """
    pending = "pending"      # Order abhi process nahi hua
    processing = "processing"  # Order process ho raha hai
    shipped = "shipped"      # Order ship ho gaya
    delivered = "delivered"  # Order deliver ho gaya
    cancelled = "cancelled"  # Order cancel ho gaya


# ========================================
# TABLE 1: Users
# ========================================
class User(Base):
    """
    Users table - saare registered users yahan store honge
    Assignment: id, full_name, email, password_hash, role, created_at
    """
    __tablename__ = "users"  # PostgreSQL mein table ka naam

    # Primary Key - har user ka unique number
    id = Column(Integer, primary_key=True, index=True)

    # User ka pura naam
    full_name = Column(String, nullable=False)

    # Email - unique hona chahiye, duplicate nahi hoga
    email = Column(String, unique=True, index=True, nullable=False)

    # Password - hashed store hoga, kabhi plain text nahi
    password_hash = Column(String, nullable=False)

    # Role - "user" ya "admin" (default: user)
    role = Column(String, default="user")

    # Kab account bana - automatically set hoga
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----------------------------------------
    # Relationships - User ke saath kya kya linked hai
    # ----------------------------------------
    # Ek user ka ek cart hoga
    cart = relationship("Cart", back_populates="user", uselist=False)

    # Ek user ke multiple orders ho sakte hain
    orders = relationship("Order", back_populates="user")


# ========================================
# TABLE 2: Categories
# ========================================
class Category(Base):
    """
    Categories table - product categories yahan hongi
    Assignment: id, name, description, created_at
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    # Category ka naam - unique hona chahiye
    name = Column(String, unique=True, nullable=False)

    # Category ki description (optional)
    description = Column(String, nullable=True)

    # Kab category bani
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----------------------------------------
    # Relationship - Is category ke products
    # ----------------------------------------
    products = relationship("Product", back_populates="category")


# ========================================
# TABLE 3: Products
# ========================================
class Product(Base):
    """
    Products table - saare products yahan honge
    Fields: id, name, description, price, stock_quantity, category_id,
            image_url (NAYA), created_at
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # Product ka naam
    name = Column(String, nullable=False)

    # Product ki detail (optional)
    description = Column(String, nullable=True)

    # Price - decimal number (e.g., 299.99)
    price = Column(Float, nullable=False)

    # Stock mein kitne hain
    stock_quantity = Column(Integer, default=0)

    # Konsi category mein hai - Category table se linked
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # ========================================
    # NAYA FIELD: Product ki picture ka path/URL
    # e.g., "uploads/products/shirt_123.jpg"
    # ========================================
    image_url = Column(String, nullable=True)

    # Kab product add hua
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----------------------------------------
    # Relationships
    # ----------------------------------------
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


# ========================================
# TABLE 4: Cart
# ========================================
class Cart(Base):
    """
    Cart table - har user ka ek cart hoga
    Assignment: id, user_id, created_at
    """
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


# ========================================
# TABLE 5: Cart Items
# ========================================
class CartItem(Base):
    """
    Cart Items table - cart mein jo products hain
    Assignment: id, cart_id, product_id, quantity
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


# ========================================
# TABLE 6: Orders
# ========================================
class Order(Base):
    """
    Orders table - placed orders yahan honge
    Assignment: id, user_id, total_amount, status, created_at
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ========================================
# TABLE 7: Order Items
# ========================================
class OrderItem(Base):
    """
    Order Items table - order mein jo products hain
    Assignment: id, order_id, product_id, quantity, price
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
