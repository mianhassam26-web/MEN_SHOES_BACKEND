# 🛍️ PrestigeWear — E-Commerce Backend API

> **FastAPI + PostgreSQL + JWT** par bana hua ek clean, production-style REST API jo kisi bhi e-commerce store (fashion/clothing brand jaisa **PrestigeWear**) ko power de sakta hai — users, products, categories, cart aur orders sab kuch ek jagah.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-14%2B-336791?logo=postgresql&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0.23-red">
  <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-black?logo=jsonwebtokens">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## ✨ Kya Khaas Hai Is Project Mein?

| | |
|---|---|
| 🔐 | JWT-based Authentication (Register / Login / Profile) |
| 👥 | Role-Based Access Control — **Admin** vs **User** |
| 🗂️ | Category Management (CRUD) |
| 👕 | Product Catalog with **Search** aur **Image Upload** |
| 🛒 | Persistent Shopping Cart per user |
| 📦 | Order Placement with automatic **stock deduction** |
| 📊 | Auto-generated **Swagger UI** & **ReDoc** documentation |
| 🧱 | Clean, layered architecture (routers → schemas → models → DB) |
| 🔁 | Alembic-powered database migrations |

Full technical breakdown neeche **[Documentation](#-full-documentation)** section mein hai — yeh README aapko sirf **5 minute mein project chalane** aur samajhne ke liye hai.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Folder Structure](#-folder-structure)
- [Database Schema](#-database-schema)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Overview](#-api-overview)
- [Authentication Flow](#-authentication-flow)
- [Example Workflow](#-example-workflow-register--shop--checkout)
- [Product Image Upload](#-product-image-upload)
- [Order Status Lifecycle](#-order-status-lifecycle)
- [Security Highlights](#-security-highlights)
- [Testing the API](#-testing-the-api)
- [Roadmap / Future Improvements](#-roadmap--future-improvements)
- [Full Documentation](#-full-documentation)
- [License](#-license)

---

## 🧰 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10+ |
| Web Framework | FastAPI | 0.104.1 |
| ASGI Server | Uvicorn | 0.24.0 |
| Database | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0.23 |
| Migrations | Alembic | 1.12.1 |
| Validation | Pydantic / pydantic-settings | 2.5.0 / 2.1.0 |
| Auth | python-jose (JWT) | 3.3.0 |
| Password Hashing | passlib + bcrypt | 1.7.4 / 4.0.1 |
| File Uploads | python-multipart | 0.0.6 |

---

## 🏗️ Project Architecture

Project ek **layered / clean architecture** pattern follow karta hai — har layer ki apni zimmedari hai, isliye code padhna aur maintain karna aasan hai:

```
Client (Browser / Postman / Frontend App)
        │
        ▼
   ┌─────────────┐
   │  Routers    │   ← HTTP endpoints (auth, products, cart, orders...)
   └─────────────┘
        │
        ▼
   ┌─────────────┐
   │  Schemas    │   ← Pydantic validation (request/response shape)
   └─────────────┘
        │
        ▼
   ┌─────────────┐
   │   Core      │   ← Security (JWT, bcrypt), Config, Dependencies
   └─────────────┘
        │
        ▼
   ┌─────────────┐
   │   Models    │   ← SQLAlchemy ORM tables
   └─────────────┘
        │
        ▼
   ┌─────────────┐
   │ PostgreSQL  │
   └─────────────┘
```

---

## 📁 Folder Structure

```
backend/
├── app/
│   ├── main.py                     # App entry point + router registration + CORS + static files
│   ├── database/
│   │   └── database.py             # Engine, SessionLocal, Base, get_db()
│   ├── models/
│   │   └── models.py               # 7 SQLAlchemy tables + OrderStatus enum
│   ├── schemas/
│   │   ├── user.py                 # UserCreate, UserLogin, UserResponse, Token
│   │   ├── category.py             # CategoryCreate, CategoryUpdate, CategoryResponse
│   │   ├── product.py              # ProductCreate, ProductUpdate, ProductResponse
│   │   ├── cart.py                 # CartItemAdd, CartItemResponse, CartResponse
│   │   └── order.py                # OrderItemResponse, OrderResponse
│   ├── routers/
│   │   ├── auth.py                 # /register, /login, /profile
│   │   ├── categories.py           # /categories
│   │   ├── products.py             # /products (+ image upload)
│   │   ├── cart.py                 # /cart
│   │   └── orders.py               # /orders
│   ├── core/
│   │   ├── config.py                # Settings (.env loader)
│   │   ├── security.py              # bcrypt hashing + JWT create/verify
│   │   └── dependencies.py          # get_current_user (auth guard)
│   ├── services/                    # Reserved for business-logic services
│   └── utils/                       # Reserved for shared helper functions
├── uploads/products/                # Uploaded product images live here
├── alembic/                         # Database migration scripts
├── alembic.ini
├── requirements.txt
├── .env                             # Environment variables (never commit this!)
└── README.md
```

---

## 🗄️ Database Schema

**7 tables**, poori tarah relational integrity ke saath:

```
users ──────1:1──────► cart
users ──────1:N──────► orders
categories ─1:N──────► products
cart ───────1:N──────► cart_items ◄──N:1── products
orders ─────1:N──────► order_items ◄─N:1── products
```

| Table | Purpose | Key Fields |
|---|---|---|
| `users` | Registered accounts | `id, full_name, email (unique), password_hash, role, created_at` |
| `categories` | Product categories | `id, name (unique), description, created_at` |
| `products` | Store catalog | `id, name, description, price, stock_quantity, category_id, image_url, created_at` |
| `cart` | One cart per user | `id, user_id (unique), created_at` |
| `cart_items` | Products inside a cart | `id, cart_id, product_id, quantity` |
| `orders` | Placed orders | `id, user_id, total_amount, status, created_at` |
| `order_items` | Snapshot of products in an order | `id, order_id, product_id, quantity, price` |

> 💡 `order_items.price` order ke waqt ki price save karta hai — agar baad mein product ki price change ho jaye to purane orders ka total sahi hi rahega.

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**
- PostgreSQL **14+**
- `pip`



### 2. Virtual Environment Banao
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Dependencies Install Karo
```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Database Banao
```sql
CREATE DATABASE prestigewear_db;
```

### 5. `.env` File Configure Karo
Root (`backend/`) mein `.env` file banao:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/prestigewear_db
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 6. Migrations Chalao
```bash
alembic upgrade head
```

### 7. Server Start Karo
```bash
uvicorn app.main:app --reload
```

### 8. Docs Kholo 🎉
```
Swagger UI  → http://localhost:8000/docs
ReDoc       → http://localhost:8000/redoc
```

---

## 🔑 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT signing secret (32+ chars, random) | `a1b2c3...` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity window | `60` |

⚠️ `.env` ko **kabhi bhi** git repo mein commit mat karo — `.gitignore` mein hona chahiye.

---

## 📡 API Overview

### 🔐 Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | Public | Naya account banao |
| POST | `/login` | Public | Login karo, JWT token lo |
| GET | `/profile` | Required | Apni profile dekho |

### 🗂️ Categories
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/categories/` | Admin | Naya category banao |
| GET | `/categories/` | Public | Sari categories list karo |
| PUT | `/categories/{id}` | Admin | Category update karo |
| DELETE | `/categories/{id}` | Admin | Category delete karo |

### 👕 Products
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/products/` | Admin | Naya product banao |
| GET | `/products/` | Public | Sare products dekho |
| GET | `/products/?search=shirt` | Public | Naam/description se search |
| GET | `/products/{id}` | Public | Single product detail |
| PUT | `/products/{id}` | Admin | Product update karo |
| DELETE | `/products/{id}` | Admin | Product delete karo (+ image cleanup) |
| POST | `/products/{id}/upload-image` | Admin | Product picture upload karo |

### 🛒 Cart
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/cart/add` | Required | Cart mein product add karo |
| GET | `/cart/` | Required | Apna cart dekho |
| DELETE | `/cart/item/{id}` | Required | Cart se item hatao |

### 📦 Orders
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/orders/` | Required | Cart se order place karo |
| GET | `/orders/` | Required | Apne sare orders dekho |
| GET | `/orders/{id}` | Required | Single order detail |
| GET | `/orders/admin/all` | Admin | **Sab** customers ke sare orders (admin panel ke liye) |

> Detailed request/response bodies, status codes aur error cases ke liye [DOCUMENTATION.md](./DOCUMENTATION.md) dekho.

---

## 🔐 Authentication Flow

Yeh API **Bearer JWT** tokens use karti hai.

```
1. POST /register  →  Account create hota hai (role = "user")
2. POST /login     →  Email + password verify hote hain → JWT token milta hai
3. Har protected request mein header bhejo:
       Authorization: Bearer <access_token>
4. Server token verify karta hai (get_current_user) aur request process karta hai
```

**Swagger UI mein test karne ka tareeqa:**
1. `/login` se token copy karo
2. Top-right **"Authorize"** button dabao
3. Token paste karo → Authorize → ab sab protected routes "Try it out" se test ho sakte hain

---

## 🧪 Example Workflow: Register → Shop → Checkout

```bash
# 1. Register
POST /register
{
  "full_name": "Ali Ahmed",
  "email": "ali@example.com",
  "password": "password123"
}

# 2. Login
POST /login
{
  "email": "ali@example.com",
  "password": "password123"
}
# → { "access_token": "...", "token_type": "bearer" }

# 3. Browse products
GET /products/?search=shirt

# 4. Add to cart
POST /cart/add
Authorization: Bearer <token>
{ "product_id": 1, "quantity": 2 }

# 5. Place order
POST /orders/
Authorization: Bearer <token>
# → cart automatically empty ho jata hai, stock kam ho jata hai
```

---

## 🖼️ Product Image Upload

Admin products ke saath image bhi attach kar sakta hai:

```
POST /products/{id}/upload-image
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data
Field: image  (File)
```

- **Allowed formats:** JPG, JPEG, PNG, GIF, WEBP
- **Max size:** 5 MB
- Image `uploads/products/` folder mein unique filename ke saath save hoti hai
- `main.py` mein `/uploads` static route mount hai — image direct browser mein khul jati hai:
  ```
  http://localhost:8000/uploads/products/product_1_abc123.jpg
  ```
- Naya upload purani image ko automatically replace/delete kar deta hai

---

## 🔄 Order Status Lifecycle

```
pending → processing → shipped → delivered
             │
             └──────► cancelled
```

| Status | Meaning |
|---|---|
| `pending` | Order place hua, abhi process nahi hua |
| `processing` | Order tayyar ho raha hai |
| `shipped` | Order dispatch ho gaya |
| `delivered` | Customer ko mil gaya |
| `cancelled` | Order cancel ho gaya |

---

## 🛡️ Security Highlights

- ✅ Passwords kabhi plain text mein store nahi hote — **bcrypt** hashing
- ✅ JWT tokens **60 minutes** baad expire hote hain (configurable)
- ✅ Role-based guards — sirf `admin` role hi sensitive actions kar sakta hai
- ✅ Users sirf apna **hi** cart aur orders dekh/edit kar sakte hain
- ✅ Order placement se pehle **stock validation** hoti hai
- ✅ Upload endpoint file **type aur size** dono validate karta hai
- ✅ `.env` secrets kabhi source control mein commit nahi hote

---

## 🧪 Testing the API

**Option 1 — Swagger UI (recommended):**
```
http://localhost:8000/docs
```

**Option 2 — curl:**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@test.com","password":"test123"}'
```

**Making a user an admin (directly in DB):**
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

---

## 🗺️ Roadmap / Future Improvements

- [ ] Refresh tokens + token revocation
- [ ] Pagination on `/products` and `/orders`
- [ ] Order status update endpoint for admins
- [ ] Payment gateway integration
- [ ] Rate limiting on auth endpoints
- [ ] Unit & integration test suite (pytest)
- [ ] Docker & docker-compose setup
- [ ] Product reviews & ratings

---

## 📖 Full Documentation

Is README mein sirf overview hai. Har module, request/response schema, error codes, security internals, aur deployment notes ke liye:

👉 **[DOCUMENTATION.md](./DOCUMENTATION.md)** dekho

---

## 📄 License

MIT License — free to use for learning and portfolio purposes.

---

<p align="center">Made with FastAPI + PostgreSQL 🚀</p>
#   M E N _ S H O E S _ B A C K E N D 
 
 #   M E N _ S H O E S _ B A C K E N D  
 #   M E N _ S H O E S _ B A C K E N D  
 