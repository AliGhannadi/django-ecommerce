# Shop API — E-Commerce Backend

A Django REST Framework e-commerce platform with JWT cookie-based authentication, Celery async tasks, Redis caching, Iranian payment gateway (Zarinpal), coupon system, and Docker deployment.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start (Docker)](#quick-start-docker)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Pagination & Filtering](#pagination--filtering)
- [Caching](#caching)
- [Celery Tasks](#celery-tasks)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

---

## Tech Stack

| Layer              | Technology                                    |
|--------------------|-----------------------------------------------|
| **Framework**      | Django 5.2 + Django REST Framework            |
| **Auth**           | SimpleJWT (cookie-based, HTTP-only)           |
| **Database**       | PostgreSQL 16                                 |
| **Cache / Broker** | Redis                                         |
| **Task Queue**     | Celery                                        |
| **Payment**        | az-iranian-bank-gateways (Zarinpal)           |
| **API Docs**       | drf-spectacular (Swagger UI + ReDoc)          |
| **Server**         | Gunicorn (prod) / runserver (dev)             |
| **Reverse Proxy**  | Nginx (prod)                                  |
| **Container**      | Docker + Docker Compose                       |
| **Testing**        | pytest + pytest-django                        |

---

## Features

### User & Authentication
- Email/password registration with email verification
- JWT access + refresh tokens stored in HTTP-only cookies
- Token refresh with optional rotation + blacklisting
- Password change and password reset via email
- Session verification endpoint
- Custom user model with vendor flag
- Profile management (first name, last name, biography, avatar)

### Products
- Full CRUD with ownership permissions
- Category tree (self-referencing parent)
- Product filtering: price range, category, discount, stock, search
- Pagination with configurable page size
- Image upload
- JSON features field for extensible product attributes

### Cart
- One cart per user
- Add / update / delete items
- Quantity tracking with stock validation via signals
- Unique product constraint per cart
- Total price calculation

### Orders
- Create orders from cart
- Address management (country, city, zipcode, address)
- Automatic total price calculation
- Coupon discount application
- Order status tracking

### Payments (Zarinpal)
- Iranian rial currency
- Sandbox mode for development
- Transaction tracking with authority codes
- Payment verification callback
- Prevents duplicate payments per order

### Coupons
- Percentage-based discounts
- Global and per-user usage limits
- Expiration dates
- General (public) and assigned (user-specific) coupons
- Atomic redemption with `select_for_update` (race-condition safe)
- Welcome coupon auto-assignment for new users

### API Documentation
- Swagger UI at `/swagger/`
- OpenAPI schema at `/schema/`
- Redoc alternative available

---

## Project Structure

```
shop/
├── core/                          # Django project root
│   ├── core/
│   │   ├── settings/
│   │   │   ├── base.py            # Shared settings
│   │   │   ├── dev.py             # Development overrides
│   │   │   ├── prod.py            # Production overrides
│   │   │   ├── env.py             # Env file loader
│   │   │   └── database.py        # DB config builder
│   │   ├── urls.py                # Root URL configuration
│   │   └── wsgi.py                # WSGI entry point
│   ├── accounts/                  # User registration, auth, profiles
│   ├── products/                  # Products, categories, filtering
│   ├── cart/                      # Shopping cart
│   ├── orders/                    # Order management
│   ├── payments/                  # Payment processing (Zarinpal)
│   ├── coupons/                   # Discount coupon system
│   ├── social/                    # Social auth (placeholder)
│   └── utils/                     # Shared utilities (exceptions, pagination)
├── envs/
│   ├── .env                       # Development environment variables
│   ├── .env.prod                  # Production environment variables
│   └── .env.sample                # Environment variable template
├── Dockerfile
├── docker-compose-dev.yml         # Development stack
├── docker-compose-prod.yml        # Production stack
├── default.conf                   # Nginx configuration
├── requirements.txt
└── .dockerignore
```

---

## Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose

### Development

```bash
# Clone the repository
git clone <repo-url> && cd shop

# Start the development stack
docker compose -f docker-compose-dev.yml up --build

# Run migrations
docker exec django python manage.py migrate

# Create a superuser
docker exec django python manage.py createsuperuser

# Run tests
docker exec django pytest
```

The API is available at `http://localhost:8000/api/v1/` and Swagger UI at `http://localhost:8000/swagger/`.

### Production

```bash
# Set up production environment variables
cp envs/.env.sample envs/.env.prod
# Edit envs/.env.prod with your production values

# Start the production stack
docker compose -f docker-compose-prod.yml up --build -d
```

---

## Environment Variables

### Core

| Variable              | Default                         | Description                      |
|-----------------------|---------------------------------|----------------------------------|
| `SECRET_KEY`          | —                               | Django secret key                |
| `DEBUG`               | `True`                          | Debug mode                       |
| `ALLOWED_HOSTS`       | `*`                             | Allowed hostnames                |
| `DJANGO_SETTINGS_MODULE` | `core.settings.dev`          | Settings module                  |

### Database

| Variable          | Default            | Description            |
|-------------------|--------------------|------------------------|
| `POSTGRES_DB`     | `shop`             | Database name          |
| `POSTGRES_USER`   | `shop`             | Database user          |
| `POSTGRES_PASSWORD` | —                | Database password      |
| `POSTGRES_HOST`   | `postgres_db`      | Database host          |
| `POSTGRES_PORT`   | `5432`             | Database port          |

### Redis / Celery

| Variable      | Default                              | Description              |
|---------------|--------------------------------------|--------------------------|
| `REDIS_HOST`  | `127.0.0.1`                          | Redis host               |
| `REDIS_PORT`  | `6379`                               | Redis port               |
| `REDIS_DB`    | `0`                                  | Redis database number    |

### JWT / Auth

| Variable                     | Default   | Description                            |
|------------------------------|-----------|----------------------------------------|
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `15`   | Access token expiry                    |
| `REFRESH_TOKEN_LIFETIME_DAYS`   | `7`    | Refresh token expiry                   |
| `AUTH_COOKIE_SECURE`         | `False`   | Secure flag on auth cookies            |
| `AUTH_COOKIE_SAMESITE`       | `Lax`     | SameSite policy                        |
| `AUTH_CSRF_AUTHENTICATION`   | `False`   | Enable CSRF for cookie auth            |

### CORS

| Variable               | Default                                                      |
|------------------------|--------------------------------------------------------------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:8000,http://127.0.0.1:5173` |

### Email

| Variable            | Default                                  |
|---------------------|------------------------------------------|
| `EMAIL_BACKEND`     | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST`        | `smtp4dev` (smtp.gmail.com in prod)       |
| `EMAIL_PORT`        | `25` (`587` in prod)                      |
| `EMAIL_USE_TLS`     | `False` (`True` in prod)                  |

### Payment

| Variable               | Description             |
|------------------------|-------------------------|
| `ZARINPAL_MERCHANT_ID` | Zarinpal merchant code  |

---

## API Endpoints

### Accounts (`/api/v1/accounts/`)

| Method | Endpoint                              | Auth     | Description                         |
|--------|---------------------------------------|----------|-------------------------------------|
| POST   | `/register`                           | —        | Register a new user                 |
| GET    | `/verify/{token}/`                    | —        | Verify email with JWT token         |
| POST   | `/login`                              | —        | Login, returns JWT in cookies       |
| POST   | `/logout`                             | —        | Clear auth cookies                  |
| POST   | `/refresh-token`                      | —        | Refresh access token                |
| POST   | `/session/verify`                     | —        | Check if current session is valid   |
| POST   | `/change-password`                    | ✓        | Change password (requires old)      |
| POST   | `/reset-password`                     | —        | Request password reset email        |
| PATCH  | `/reset-password/set-password`        | —        | Set new password with token         |

### Products (`/api/v1/products/`)

| Method | Endpoint                  | Auth         | Description                    |
|--------|---------------------------|--------------|--------------------------------|
| GET    | `/`                       | —            | List products (paginated)      |
| POST   | `/`                       | ✓ (vendor)   | Create product                 |
| GET    | `/{id}/`                  | —            | Retrieve product               |
| PUT    | `/{id}/`                  | ✓ (owner)    | Update product                 |
| PATCH  | `/{id}/`                  | ✓ (owner)    | Partial update product         |
| DELETE | `/{id}/`                  | ✓ (owner)    | Delete product                 |
| POST   | `/{id}/add_to_cart/`      | ✓            | Add product to cart            |

**Query parameters for listing:**
- `search` — search title, description, brief_description
- `min_price` / `max_price` — price range
- `min_discount` / `max_discount` — discount range
- `min_quantity` / `max_quantity` — stock range
- `in_stock` — `true` or `false`
- `category` — category ID
- `category_name` — category name (partial match)
- `title` — exact or partial match
- `is_published` — `true` or `false`
- `user` — vendor user ID

### Cart (`/api/v1/cart/`)

| Method | Endpoint            | Auth | Description                |
|--------|---------------------|------|----------------------------|
| GET    | `/`                 | ✓    | List cart items            |
| PATCH  | `/update_item/`     | ✓    | Update item quantity       |
| DELETE | `/delete_item/`     | ✓    | Remove item from cart      |
| DELETE | `/clear/`           | ✓    | Clear entire cart          |

### Orders (`/api/v1/orders/`)

| Method | Endpoint     | Auth | Description        |
|--------|--------------|------|--------------------|
| GET    | `/`          | ✓    | List user orders   |
| POST   | `/`          | ✓    | Create order       |
| GET    | `/{id}/`     | ✓    | Retrieve order     |
| PUT    | `/{id}/`     | ✓    | Update order       |
| PATCH  | `/{id}/`     | ✓    | Partial update     |
| DELETE | `/{id}/`     | ✓    | Delete order       |

### Payments (`/api/v1/payments/`)

| Method | Endpoint     | Auth | Description                    |
|--------|--------------|------|--------------------------------|
| POST   | `/process/`  | ✓    | Initiate Zarinpal payment      |
| GET    | `/callback/` | —    | Zarinpal payment callback      |

### Coupons (`/api/v1/coupons/`)

| Method | Endpoint                       | Auth | Description                          |
|--------|--------------------------------|------|--------------------------------------|
| GET    | `/`                            | —    | List available coupons               |
| GET    | `/{id}/`                       | —    | Retrieve coupon details              |
| GET    | `/{id}/validate_coupon/`       | —    | Validate coupon (returns valid flag) |

---

## Authentication

This project uses JWT (JSON Web Tokens) stored in HTTP-only cookies.

### Flow

1. **Register** at `POST /api/v1/accounts/register` — receive verification email
2. **Verify** email via the link sent to your inbox
3. **Login** at `POST /api/v1/accounts/login` — sets `access_token` and `refresh_token` cookies
4. **Authenticated requests** — cookies are sent automatically by the browser
5. **Refresh** at `POST /api/v1/accounts/refresh-token` — rotates the access token
6. **Logout** at `POST /api/v1/accounts/logout` — clears all auth cookies

### Cookie Configuration

| Cookie            | HTTP-only | SameSite | Secure (prod) |
|-------------------|-----------|----------|---------------|
| `access_token`    | ✓         | Lax      | ✓             |
| `refresh_token`   | ✓         | Lax      | ✓             |
| `csrftoken`       | ✗         | Lax      | ✓             |

Access tokens expire in 15 minutes (configurable). Refresh tokens expire in 7 days (configurable). In production, refresh token rotation and blacklisting are enabled.

---

## Pagination & Filtering

### Pagination

Products are paginated using `PageNumberPagination`. Responses include:

```json
{
  "links": {
    "next": "http://.../?page=2",
    "previous": null
  },
  "total_objects": 42,
  "total_pages": 3,
  "results": [...]
}
```

Use `?page=<number>` to navigate pages.

### Filtering

Products support filtering via `django-filter`. See the [Products endpoints](#products-apiv1products) section for available query parameters.

---

## Caching

Redis-backed caching with the following policies:

| Endpoint          | Duration | Key Prefix       | Invalidation                               |
|-------------------|----------|------------------|--------------------------------------------|
| Product list      | 5 min    | `product_list`   | Cleared on Product save/delete             |
| Cart list         | 15 min   | `cart_list`      | Cleared on Cart save/delete                |

---

## Celery Tasks

| Task                | Trigger                            | Description                        |
|---------------------|------------------------------------|------------------------------------|
| `email_verification`| User registration                  | Sends verification email           |
| Coupon assignment   | New user registration (signal)     | Assigns welcome coupon             |

---

## Testing

```bash
# Run all tests
docker exec django pytest

# Run tests for a specific app
docker exec django pytest products/tests.py -v

# Run with coverage
docker exec django pytest --cov=.
```

The test suite includes 117+ tests across all apps (accounts, products, cart, orders, payments, coupons).

### Test Configuration

- Database: `--reuse-db` (preserves test DB between runs)
- Migrations: `--nomigrations` (uses `migrate`-equivalent SQL directly)
- Settings: `core.settings.dev`

---

## Deployment

### Production Stack

```
User → Nginx (port 80) → Gunicorn (port 8000) → Django
                     ↕                    ↕
               Static/Media          Redis (cache + broker)
                                       ↕   ↕
                                  PostgreSQL  Celery
```

### Steps

1. Copy and edit the production environment file:

```bash
cp envs/.env.sample envs/.env.prod
# Edit with your production values
```

2. Build and start:

```bash
docker compose -f docker-compose-prod.yml up --build -d
```

3. Run migrations:

```bash
docker exec django python manage.py migrate
```

4. Collect static files (done automatically on startup).

### Key Production Settings

| Setting                    | Value           |
|----------------------------|-----------------|
| `DEBUG`                    | `False`         |
| `SECRET_KEY`               | From env        |
| `SESSION_COOKIE_SECURE`    | `True`          |
| `CSRF_COOKIE_SECURE`       | `True`          |
| `SECURE_SSL_REDIRECT`      | `True`          |
| `AUTH_COOKIE_SECURE`       | `True`          |
| `SHOW_SWAGGER`             | `False`         |
| `DISABLE_BROWSEABLE_API`   | `True`          |

---

## License

MIT License
