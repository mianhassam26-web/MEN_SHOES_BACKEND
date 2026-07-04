# 📚 PrestigeWear Backend — Complete Technical Documentation

Yeh document project ka **har layer**, **har endpoint**, aur **har design decision** detail mein cover karta hai. README.md quick-start ke liye hai; yeh file deep reference ke liye hai — jaise ek internal engineering wiki.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Deep Dive](#2-architecture-deep-dive)
3. [Database Design](#3-database-design)
4. [Configuration & Environment](#4-configuration--environment)
5. [Authentication & Security Internals](#5-authentication--security-internals)
6. [Module-by-Module Reference](#6-module-by-module-reference)
7. [API Reference (Full Detail)](#7-api-reference-full-detail)
8. [File Upload Subsystem](#8-file-upload-subsystem)
9. [Business Logic Notes](#9-business-logic-notes)
10. [Error Handling Reference](#10-error-handling-reference)
11. [Database Migrations (Alembic)](#11-database-migrations-alembic)
12. [Deployment Guide](#12-deployment-guide)
13. [Known Limitations](#13-known-limitations)
14. [Glossary](#14-glossary)

---

## 1. System Overview

PrestigeWear Backend ek **monolithic REST API** hai jo FastAPI par bana hai, aur ek fashion/clothing e-commerce store ke core operations handle karta hai:

- Customer accounts (registration, login, profile)
- Product catalog management (with images)
- Category organization
- Shopping cart per customer
- Order placement with inventory control

Yeh **stateless** API hai — koi server-side session store nahi hota; authentication har request ke saath JWT token ke zariye hoti hai.

---

## 2. Architecture Deep Dive

### 2.1 Request Lifecycle

```
1. Client → HTTP Request (with/without Authorization header)
2. FastAPI routing → matched router function
3. Dependency injection resolves:
     - get_db()            → SQLAlchemy session
     - get_current_user()  → decodes JWT, loads User row (if route is protected)
4. Pydantic schema validates request body (if any)
5. Router function executes business logic
6. SQLAlchemy ORM performs DB operations
7. Response serialized through Pydantic response_model
8. JSON returned to client
```

### 2.2 Layers & Responsibilities

| Layer | Directory | Responsibility |
|---|---|---|
| **Routers** | `app/routers/` | HTTP verb + path mapping, request orchestration, HTTPExceptions |
| **Schemas** | `app/schemas/` | Input validation & output shaping (Pydantic models) |
| **Core** | `app/core/` | Cross-cutting concerns: config, JWT, password hashing, auth guard |
| **Models** | `app/models/` | SQLAlchemy ORM table definitions & relationships |
| **Database** | `app/database/` | Engine/session lifecycle management |
| **Services** | `app/services/` | Reserved for extracted business logic (currently empty scaffold) |
| **Utils** | `app/utils/` | Reserved for shared helper functions (currently empty scaffold) |

### 2.3 Dependency Injection Graph

```
get_current_user
    ├── depends on: bearer_scheme (HTTPBearer)
    └── depends on: get_db

Every protected router function
    └── depends on: get_current_user (which itself depends on get_db)

Every DB-touching router function
    └── depends on: get_db
```

`get_db()` is a **generator dependency** — FastAPI opens a new SQLAlchemy `Session` per request and guarantees it's closed via `try/finally`, even if the handler raises an exception.

---

## 3. Database Design

### 3.1 Entity Relationship Diagram (textual)

```
┌───────────┐        ┌────────────┐
│  users    │1──────1│    cart    │
└───────────┘        └────────────┘
     │1                    │1
     │                     │N
     │N               ┌────────────┐      N ┌────────────┐
     │            ┌──►│ cart_items │◄───────│  products  │
┌───────────┐     │   └────────────┘        └────────────┘
│  orders   │     │                                │N
└───────────┘     │                                │
     │1            │                                │1
     │N            │                          ┌────────────┐
┌────────────┐     │                          │ categories │
│order_items │◄────┘ (N products referenced)  └────────────┘
└────────────┘
```

### 3.2 Table Definitions

#### `users`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, index |
| full_name | String | NOT NULL |
| email | String | UNIQUE, NOT NULL, index |
| password_hash | String | NOT NULL (bcrypt hash, never plaintext) |
| role | String | default `"user"` (values: `user` \| `admin`) |
| created_at | DateTime(tz) | server default `now()` |

#### `categories`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| name | String | UNIQUE, NOT NULL |
| description | String | nullable |
| created_at | DateTime(tz) | server default `now()` |

#### `products`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| name | String | NOT NULL |
| description | String | nullable |
| price | Float | NOT NULL |
| stock_quantity | Integer | default 0 |
| category_id | Integer | FK → `categories.id`, nullable |
| image_url | String | nullable — set via upload endpoint |
| created_at | DateTime(tz) | server default `now()` |

#### `cart`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| user_id | Integer | FK → `users.id`, UNIQUE (one cart per user) |
| created_at | DateTime(tz) | server default `now()` |

#### `cart_items`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| cart_id | Integer | FK → `cart.id` |
| product_id | Integer | FK → `products.id` |
| quantity | Integer | default 1 |

#### `orders`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| user_id | Integer | FK → `users.id` |
| total_amount | Float | NOT NULL |
| status | Enum(`OrderStatus`) | default `pending` |
| created_at | DateTime(tz) | server default `now()` |

`OrderStatus` enum values: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.

#### `order_items`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK |
| order_id | Integer | FK → `orders.id` |
| product_id | Integer | FK → `products.id` |
| quantity | Integer | NOT NULL |
| price | Float | NOT NULL — **price snapshot at time of order** |

### 3.3 Cascade Behavior

- `Cart.items` → `cascade="all, delete-orphan"`: cart delete hone par uske cart_items bhi delete ho jate hain.
- `Order.order_items` → `cascade="all, delete-orphan"`: order delete hone par uske order_items bhi delete ho jate hain.

---

## 4. Configuration & Environment

`app/core/config.py` mein `Settings` class (`pydantic_settings.BaseSettings`) `.env` file se values load karti hai automatically.

| Setting | Type | Required | Default |
|---|---|---|---|
| `DATABASE_URL` | str | ✅ | — |
| `SECRET_KEY` | str | ✅ | — |
| `ALGORITHM` | str | ❌ | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | ❌ | `60` |

Settings object app-wide singleton hai (`settings = Settings()`), jo `security.py`, `database.py` waghera sab jagah import hota hai.

---

## 5. Authentication & Security Internals

### 5.1 Password Hashing (`core/security.py`)

- Uses `passlib.CryptContext` with the `bcrypt` scheme.
- bcrypt ki hard limit **72 bytes** hoti hai — is liye password ko hash karne aur verify karne se pehle explicitly `.encode("utf-8")[:72]` se truncate kiya jata hai (dono jagah consistently, taake hashing/verification match ho).

### 5.2 JWT Token Lifecycle

- `create_access_token(data)`:
  - Payload mein `sub` claim = user's email
  - `exp` claim = `now + ACCESS_TOKEN_EXPIRE_MINUTES`
  - Signed using `SECRET_KEY` with `HS256` (or configured algorithm)
- `verify_token(token)`:
  - Decodes & validates signature/expiry
  - Returns email (`sub` claim) or `None` on failure (`JWTError` caught)

### 5.3 Auth Guard (`core/dependencies.py`)

`get_current_user`:
1. Extracts raw token from `Authorization: Bearer <token>` header (via `HTTPBearer`)
2. Calls `verify_token()`
3. Agar invalid/expired → `401 Unauthorized`
4. Agar valid → email se `User` row query hoti hai
5. Agar user DB mein nahi mila → `401 Unauthorized`
6. Return `User` ORM instance → injected into route handler

### 5.4 Role-Based Authorization

Har router (`categories.py`, `products.py`, `orders.py`) mein ek local `check_admin(current_user)` helper hai jo `current_user.role != "admin"` par `403 Forbidden` raise karta hai. Yeh pattern **route-level guard** hai — `get_current_user` sirf authentication karta hai, authorization (role check) explicitly route ke andar hoti hai.

> 📝 Note: `check_admin` currently har router file mein duplicate defined hai. Ise `app/core/dependencies.py` mein consolidate karna future refactor ke liye ek accha candidate hai (see [Known Limitations](#13-known-limitations)).

---

## 6. Module-by-Module Reference

### `app/main.py`
- FastAPI app instance banata hai (`title`, `description`, `version`)
- CORS middleware enable karta hai — currently `allow_origins=["*"]` (dev-friendly, **production mein restrict karna zaroori hai**)
- `/uploads` path ko `StaticFiles` se mount karta hai taake uploaded images directly serve ho sakein
- Root `GET /` health-check route
- Sab 5 routers (`auth`, `categories`, `products`, `cart`, `orders`) register karta hai

### `app/database/database.py`
- `engine` = `create_engine(DATABASE_URL)`
- `SessionLocal` = sessionmaker with `autocommit=False, autoflush=False`
- `Base` = declarative base jisse saare models inherit karte hain
- `get_db()` generator — per-request session lifecycle

### `app/models/models.py`
- 7 ORM classes + `OrderStatus` enum (poori detail Section 3 mein)

### `app/core/config.py`, `security.py`, `dependencies.py`
- Detail Section 4 & 5 mein cover ho chuki hai

### `app/schemas/*.py`
- Har resource ke liye 3 tarah ke schemas: `*Create` (input), `*Update` (partial input), `*Response` (output, `from_attributes=True` taake ORM objects seedha serialize ho sakein)
- `CartItemResponse` aur `OrderItemResponse` nested `ProductResponse` include karte hain — is se frontend ko cart/order dekhne ke liye alag se product API call nahi karni padti

### `app/routers/*.py`
- Full endpoint detail Section 7 mein

---

## 7. API Reference (Full Detail)

> Base URL (local dev): `http://localhost:8000`

### 7.1 Authentication

#### `POST /register`
Create a new user account (role always defaults to `"user"`).

**Request Body**
```json
{
  "full_name": "Ali Ahmed",
  "email": "ali@example.com",
  "password": "mypassword123"
}
```

**Response `201 Created`**
```json
{
  "id": 1,
  "full_name": "Ali Ahmed",
  "email": "ali@example.com",
  "role": "user",
  "created_at": "2026-07-02T10:00:00Z"
}
```

**Errors:** `400` if email already registered.

---

#### `POST /login`
Authenticate and receive a JWT access token.

**Request Body**
```json
{ "email": "ali@example.com", "password": "mypassword123" }
```

**Response `200 OK`**
```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

**Errors:** `401` if email/password incorrect.

---

#### `GET /profile` 🔒
Return the authenticated user's own profile.

**Response `200 OK`** — same shape as `/register` response.

---

### 7.2 Categories

#### `POST /categories/` 🔒👑
Create a category (admin only).
```json
{ "name": "Electronics", "description": "Electronic products" }
```
**Errors:** `400` duplicate name · `403` not admin

#### `GET /categories/`
List all categories. No auth required.

#### `PUT /categories/{category_id}` 🔒👑
Partial update — only send fields you want to change.
**Errors:** `404` not found · `403` not admin

#### `DELETE /categories/{category_id}` 🔒👑
**Errors:** `404` not found · `403` not admin

---

### 7.3 Products

#### `POST /products/` 🔒👑
```json
{
  "name": "Polo Shirt",
  "description": "Premium cotton polo",
  "price": 29.99,
  "stock_quantity": 100,
  "category_id": 1
}
```
`image_url` is always `null` on creation — set it afterwards via the upload endpoint.
**Errors:** `404` category doesn't exist · `403` not admin

#### `GET /products/`
Query params:
- `search` (optional, string) — case-insensitive match against `name` OR `description` (`ILIKE %term%`)

Examples: `/products/?search=shirt`, `/products/`

#### `GET /products/{product_id}`
Single product with `image_url`. **Errors:** `404`

#### `PUT /products/{product_id}` 🔒👑
Partial update (all fields optional). **Errors:** `404` product/category not found · `403` not admin

#### `DELETE /products/{product_id}` 🔒👑
Deletes the product row **and** its uploaded image file from disk (if any).
**Errors:** `404` · `403` not admin

#### `POST /products/{product_id}/upload-image` 🔒👑
`multipart/form-data`, field name `image`. Full detail in [Section 8](#8-file-upload-subsystem).

---

### 7.4 Cart

#### `POST /cart/add` 🔒
```json
{ "product_id": 1, "quantity": 2 }
```
Behavior:
- Creates a cart for the user automatically if one doesn't exist yet
- If the product is already in the cart, quantity is **incremented** (not overwritten)
- Validates stock availability before adding

**Errors:** `404` product not found · `400` insufficient stock

#### `GET /cart/` 🔒
Returns the user's cart with nested items and nested product details. Auto-creates an empty cart if none exists.

#### `DELETE /cart/item/{item_id}` 🔒
`item_id` = the `cart_items.id`, **not** the product id. Ownership is verified — you can only delete items from your own cart.

**Errors:** `404` cart or item not found / not yours

---

### 7.5 Orders

#### `POST /orders/` 🔒
Converts the current cart into an order:
1. Validates cart is not empty
2. Loops through cart items, validating stock for each
3. Calculates `total_amount`
4. Creates `Order` + `OrderItem` rows (price is **snapshotted** from the product at that moment)
5. Decrements `stock_quantity` on each product
6. Empties the cart

**Errors:** `400` empty cart / insufficient stock · `404` product missing mid-transaction

#### `GET /orders/` 🔒
Only the current user's own orders.

#### `GET /orders/{order_id}` 🔒
Single order — scoped to the current user (others' orders return `404`, not `403`, to avoid leaking existence).

#### `GET /orders/admin/all` 🔒👑
Returns **every** order from **every** user — intended for an admin dashboard.
**Errors:** `403` not admin

> Legend: 🔒 = requires login, 👑 = requires `admin` role

---

## 8. File Upload Subsystem

### 8.1 Storage Strategy
- Local filesystem storage under `uploads/products/`
- No cloud storage (S3, etc.) — **suitable for development/small deployments only**
- Files are served via FastAPI's `StaticFiles` mount at `/uploads`

### 8.2 Upload Validation Rules
| Rule | Value |
|---|---|
| Allowed extensions | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` |
| Max file size | 5 MB (5 × 1024 × 1024 bytes) |
| Filename strategy | `product_{id}_{uuid4().hex}{ext}` — collision-proof |

### 8.3 Upload Flow
```
1. Admin-only check
2. Product existence check (404 if missing)
3. Extension check against ALLOWED_EXTENSIONS (400 if invalid)
4. Read full file into memory, check size (400 if > 5MB)
5. If product already has an image → delete the old file from disk
6. Generate unique filename, write bytes to disk
7. Update product.image_url = "/uploads/products/<filename>"
8. Commit and return updated ProductResponse
```

⚠️ **Note:** the entire file is read into memory (`await image.read()`) before size validation — for very large files this isn't memory-efficient, but is acceptable given the 5 MB cap.

---

## 9. Business Logic Notes

### 9.1 Cart → Order Conversion Is Transactional in Intent
The order creation flow uses `db.flush()` after creating the `Order` (to get its generated `id` before committing) and defers the final `db.commit()` until all `OrderItem` rows and stock decrements are staged. This keeps the operation logically atomic within a single SQLAlchemy session — if an exception is raised mid-loop, nothing is persisted since `commit()` is never reached.

### 9.2 Price Snapshotting
`order_items.price` stores the product's price **at the time of purchase**, not a live reference to `products.price`. This is intentional — it keeps historical order totals accurate even if the admin later changes product pricing.

### 9.3 Stock Consistency
Both `POST /cart/add` and `POST /orders/` independently validate stock — this means a user can add more to their cart than is available only if stock changes *after* it was added but *before* checkout, in which case order placement will correctly reject it.

---

## 10. Error Handling Reference

| HTTP Code | Meaning in this API | Typical Trigger |
|---|---|---|
| `400 Bad Request` | Business rule violation | Duplicate email/category, insufficient stock, empty cart, bad file type/size |
| `401 Unauthorized` | Auth failure | Missing/invalid/expired token, wrong login credentials |
| `403 Forbidden` | Authorization failure | Non-admin hitting an admin-only route |
| `404 Not Found` | Resource missing | Invalid id for user/category/product/cart item/order |
| `422 Unprocessable Entity` | Validation failure | Request body doesn't match the Pydantic schema (auto-generated by FastAPI) |

All errors follow FastAPI's standard shape:
```json
{ "detail": "human-readable message (Roman Urdu in this project)" }
```

---

## 11. Database Migrations (Alembic)

- Config: `alembic.ini` + `alembic/env.py`
- Migration scripts: `alembic/versions/`
- Notable migration: `add_image_url_to_products.py` — adds the `image_url` column to `products` (needed if you're upgrading an existing database that predates the image-upload feature)

**Common commands:**
```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after changing models.py
alembic revision --autogenerate -m "description of change"

# Roll back one revision
alembic downgrade -1
```

---

## 12. Deployment Guide

### 12.1 Minimal Production Checklist
- [ ] Set `allow_origins` in `main.py` CORS middleware to your actual frontend domain(s) — **not** `"*"`
- [ ] Use a strong, randomly generated `SECRET_KEY` (32+ characters)
- [ ] Store secrets in your platform's secret manager, not a committed `.env`
- [ ] Run behind a production ASGI setup, e.g.:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
  or use Gunicorn with Uvicorn workers for multi-process serving
- [ ] Put a reverse proxy (Nginx/Caddy) in front for TLS termination
- [ ] Move uploaded images to object storage (S3-compatible) for scalability instead of local disk
- [ ] Enable PostgreSQL connection pooling appropriate for your traffic
- [ ] Set up structured logging and error monitoring (e.g., Sentry)

### 12.2 Suggested Environment Separation
| Environment | DATABASE_URL points to | CORS origins |
|---|---|---|
| Development | local PostgreSQL | `*` (fine for local only) |
| Staging | staging DB | staging frontend URL |
| Production | production DB (managed, backed up) | production frontend URL only |

---

## 13. Known Limitations

- `check_admin()` helper is duplicated across `categories.py`, `products.py`, and `orders.py` instead of being centralized in `core/dependencies.py`.
- No pagination on list endpoints (`/products/`, `/orders/`, `/categories/`) — fine for small catalogs, will need `limit`/`offset` or cursor pagination at scale.
- No endpoint for an admin to update order `status` (e.g., mark as `shipped`) — orders currently stay `pending` until manually changed in the database.
- No refresh-token mechanism — tokens simply expire after `ACCESS_TOKEN_EXPIRE_MINUTES` and the user must log in again.
- CORS is wide open (`*`) by default — must be locked down before production use.
- Uploaded images are stored on local disk, which doesn't scale horizontally across multiple server instances without shared storage.
- No automated test suite currently included in the project.

---

## 14. Glossary

| Term | Meaning |
|---|---|
| **JWT** | JSON Web Token — a signed token used to authenticate requests without server-side sessions |
| **ORM** | Object-Relational Mapper — SQLAlchemy translates Python classes into SQL tables |
| **Bearer Token** | An auth scheme where the client sends `Authorization: Bearer <token>` on each request |
| **Migration** | A versioned script that changes the database schema (via Alembic) |
| **Dependency Injection (FastAPI)** | Pattern where reusable logic (like `get_db`, `get_current_user`) is declared as a function and "injected" into route handlers via `Depends(...)` |
| **Price Snapshot** | Storing a price value at a point in time (in `order_items`) so it doesn't change retroactively |

---

<p align="center">— End of Documentation —</p>
