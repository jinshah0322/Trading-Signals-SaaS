# Trading Signals SaaS Platform

A full-stack web application that provides Trading signals with a premium plan as well. Built with React, FastAPI, PostgreSQL, Redis, and Stripe integration.

🌐 **Live Demo:** [http://13.204.77.91](http://13.204.77.91)  
🏢 **Hosted on:** AWS EC2  

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Setup](#environment-setup)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Stripe Webhook Setup](#stripe-webhook-setup)

---

## ✨ Features

### User Management
- 🔐 **Secure Authentication** - JWT-based auth with bcrypt password hashing
- 📧 **Email Validation** - Validates email format and uniqueness
- 🔑 **Strong Password Policy** - Backend validation enforces:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character (!@#$%^&*(),.?":{}|<>)
- ✅ **Frontend Validation** - Minimum 6 characters with confirmation field

### Trading Signals
- 📊 **Free Tier** - Access to 3 trading signals
- 💎 **Premium Tier** - Full access to all 20 trading signals
- ⚡ **Smart Caching** - Signals cached in Redis for 5 minutes (300 seconds)
- 🎯 **Actionable Insights** - Symbol, action (BUY/SELL), entry price, 3% target, 2% stop loss
- 📈 **20 Instruments** - NIFTY, BANKNIFTY, RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, and more
- 🤖 **Mock Data Generation** - 2-second simulated computation with ±2% price variation

### Payment Integration
- 💳 **Stripe Checkout** - Secure payment processing (one-time payment mode)
- 🔄 **Webhook Handling** - Automatic subscription activation via webhooks
- ✅ **Idempotency** - Prevents duplicate webhook processing (24-hour cache)
- 💰 **Pricing** - ₹499 one-time payment for lifetime access

### Security & Performance
- 🚦 **Rate Limiting** - Redis-based rate limiting on auth endpoints
- 🔒 **JWT Authorization** - Protected API endpoints
- 💾 **Connection Pooling** - Optimized database and Redis connections
- 🏃 **Async Operations** - Non-blocking I/O for high performance

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS EC2 Instance                     │
│                                                              │
│  ┌───────────────┐                                          │
│  │    Nginx      │  (Reverse Proxy)                        │
│  │  Port 80      │                                          │
│  └───────┬───────┘                                          │
│          │                                                   │
│          ├─────────────────────────────────────┐           │
│          │                                      │           │
│          ▼                                      ▼           │
│  ┌─────────────────┐                 ┌─────────────────┐  │
│  │  React Frontend  │                 │  FastAPI Backend │  │
│  │  Docker:3000→80  │────────────────▶│  Docker:8000     │  │
│  │  (Nginx Server)  │   API Calls     │  (Uvicorn)       │  │
│  └─────────────────┘                 └────────┬──────────┘  │
│                                                │             │
│                    ┌───────────────────────────┴──────┐     │
│                    │                                   │     │
│                    ▼                                   ▼     │
│          ┌──────────────────┐              ┌───────────────┐│
│          │   PostgreSQL     │              │     Redis     ││
│          │   Database       │              │     Cache     ││
│          │   Docker:5432    │              │  Docker:6379  ││
│          └──────────────────┘              └───────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Docker Bridge Network                    │  │
│  │  All containers communicate via trading_network      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │  Webhooks
                           ▼
                   ┌───────────────┐
                   │  Stripe API   │
                   │  (External)   │
                   └───────────────┘
```

### Request Flow

1. **User Request** → Nginx (80) → Frontend (127.0.0.1:3000)
2. **API Call** → Frontend → Backend (/api/* → http://backend:8000)
3. **Authentication** → JWT validation via Redis cache
4. **Rate Limiting** → Check Redis for IP/email limits
5. **Database Query** → PostgreSQL connection pool
6. **Response** → JSON data → Frontend → User

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 19.2 with Vite
- **Routing:** React Router DOM v7
- **UI:** Bootstrap 5.3 + Bootstrap Icons
- **Notifications:** React Toastify
- **Build Tool:** Vite 7.2
- **Server:** Nginx (Alpine)

### Backend
- **Framework:** FastAPI 0.109
- **Language:** Python 3.12
- **Server:** Uvicorn with auto-reload
- **Database:** asyncpg for PostgreSQL
- **Cache:** redis-py with hiredis
- **Authentication:** python-jose (JWT) + passlib (bcrypt)
- **Payments:** Stripe SDK 7.11
- **Validation:** Pydantic 2.5

### Infrastructure
- **Database:** PostgreSQL 15 (Alpine)
- **Cache:** Redis 7 (Alpine)
- **Containerization:** Docker & Docker Compose
- **Reverse Proxy:** Nginx (AWS EC2)
- **Cloud:** AWS EC2 Instance
- **Testing:** pytest 7.4 + httpx

---

## 📁 Project Structure

```
Trading-Signals-SaaS/
├── docker-compose.yml              # Multi-container orchestration
├── README.md                       
│
├── Trading Signals Backend/
│   ├── Dockerfile                  # Backend container config
│   ├── requirements.txt            # Python dependencies
│   ├── init.sql                    # Database schema
│   ├── pytest.ini                  # Pytest configuration
│   ├── .env                        # Environment variables (not in repo)
│   ├── .env.example                # Environment template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py               # Settings management
│   │   ├── database.py             # PostgreSQL connection pool
│   │   ├── redis_client.py         # Redis connection pool
│   │   ├── dependencies.py         # Reusable dependencies (auth)
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py       # Redis-based rate limiting
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Auth request/response models
│   │   │   ├── user.py             # User models
│   │   │   ├── billing.py          # Payment models
│   │   │   └── signal.py           # Signal models
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Signup, Login, /me
│   │   │   ├── billing.py          # Checkout, Webhooks, Status
│   │   │   └── signals.py          # Get trading signals
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth_service.py     # User management, JWT
│   │       ├── stripe_service.py   # Payment processing
│   │       ├── signal_service.py   # Signal generation
│   │       └── redis_service.py    # Rate limiting logic
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # Pytest fixtures
│       └── test_auth.py            # Authentication tests (9 tests)
│
└── Trading Signals Frontend/
    ├── Dockerfile                  # Multi-stage build (Node + Nginx)
    ├── nginx.conf                  # Nginx configuration
    ├── package.json                # NPM dependencies
    ├── vite.config.js              # Vite configuration
    ├── index.html                  # Entry HTML
    │
    ├── public/                     # Static assets
    │
    └── src/
        ├── main.jsx                # React entry point
        ├── App.jsx                 # Main app component
        ├── index.css               # Global styles
        │
        ├── components/
        │   ├── Navbar.jsx          # Navigation bar
        │   ├── Loader.jsx          # Loading spinner
        │   └── PrivateRoute.jsx    # Auth guard
        │
        ├── pages/
        │   ├── Signup.jsx          # User registration
        │   ├── Login.jsx           # User login
        │   ├── Dashboard.jsx       # Trading signals display
        │   ├── Success.jsx         # Payment success page
        │   └── Cancel.jsx          # Payment cancel page
        │
        └── utils/
            ├── api.js              # API client functions
            └── auth.js             # Auth helper functions
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** 20.10+ & **Docker Compose** v2
- **Node.js** 20+ (for local frontend development)
- **Python** 3.12+ (for local backend development)
- **Git** for version control
- **Stripe Account** for payment processing

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd Trading-Signals-SaaS
```

2. **Set up environment variables(Backend)**
```bash
cd "Trading Signals Backend"
cp .env.example .env
# Edit .env with your actual values
```

3. **Set up environment variables(Frontend)**
```bash
cd "Trading Signals Frontend"
cp .env.example .env
# Edit .env with your actual values
```

4. **Start all services**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ⚙️ Environment Setup

Create a `.env` file in `Trading Signals Backend/` directory:

```bash
# App Configuration
APP_NAME="Trading Signals SaaS"
DEBUG=true

# Database (Docker service name when using Docker)
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/trading_signals

# Redis (Docker service name when using Docker)
REDIS_URL=redis://redis:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
STRIPE_PRICE_ID=price_your_stripe_price_id

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens | Use strong random string |
| `JWT_ACCESS_TOKEN_EXPIRE_DAYS` | Token expiration in days | `7` |
| `STRIPE_SECRET_KEY` | Stripe API secret key | `sk_test_...` or `sk_live_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe API public key | `pk_test_...` or `pk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature secret | `whsec_...` |
| `STRIPE_PRICE_ID` | Stripe subscription price ID | `price_...` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

---

## 🐳 Running with Docker

### Development Mode

Start all services with hot-reload:

```bash
docker-compose up
```

Backend changes auto-reload via volume mount:
```yaml
volumes:
  - ./Trading Signals Backend/app:/app/app
```

### Production Build

Build and run optimized images:

```bash
docker-compose up --build -d
```

### Individual Services

Start specific services:

```bash
# Database only
docker-compose up postgres

# Backend only (requires postgres & redis)
docker-compose up backend

# Frontend only (requires backend)
docker-compose up frontend
```

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v

# Rebuild specific service
docker-compose up --build backend

# Execute commands in containers
docker exec -it trading_signals_backend bash
docker exec -it trading_signals_frontend sh
docker exec -it trading_signals_db psql -U postgres -d trading_signals

# View container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

---

## 🧪 Testing

The project includes comprehensive pytest tests for authentication endpoints.

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures and setup
└── test_auth.py         # 9 authentication tests
```

### Test Coverage

**9 Tests Covering:**
1. ✅ Successful signup with strong password
2. ✅ Duplicate email validation
3. ✅ Weak password rejection (5 scenarios)
4. ✅ Successful login
5. ✅ Invalid credentials handling
6. ✅ Non-existent user handling
7. ✅ Authenticated /me endpoint
8. ✅ Missing token validation
9. ✅ Invalid token validation

### Running Tests

**From host machine:**
```bash
docker exec -it trading_signals_backend pytest -v
```

**From inside container:**
```bash
docker exec -it trading_signals_backend bash
pytest -v
```

**Specific test file:**
```bash
docker exec -it trading_signals_backend pytest tests/test_auth.py -v
```

**Specific test:**
```bash
docker exec -it trading_signals_backend pytest tests/test_auth.py::TestAuthEndpoints::test_signup_success -v
```

**With coverage:**
```bash
docker exec -it trading_signals_backend pytest --cov=app tests/
```

### Test Configuration

Tests use:
- **Real HTTP requests** to `localhost:8000` (running backend)
- **Automatic rate limit clearing** before each test
- **Random test emails** to avoid conflicts
- **Automatic cleanup** of test data

**Key Fixtures:**
- `event_loop`: Session-scoped async event loop
- `clear_rate_limits`: Clears Redis before each test
- `client`: HTTP client for API calls
- `test_user_data`: Random test credentials
- `cleanup_test_user`: Deletes test users after tests

---

## 📚 API Documentation

### Base URL

- **Local:** `http://localhost:8000`
- **Production:** `http://13.204.77.91/api`

### Interactive API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Authentication Endpoints

#### POST /auth/signup
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_paid": false,
    "created_at": "2026-01-19T10:30:00"
  }
}
```

**Rate Limit:** 5 requests per 15 minutes per IP

#### POST /auth/login
Authenticate existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):** Same as signup

**Rate Limit:** 5 requests per 15 minutes per email

#### GET /auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_paid": false,
  "created_at": "2026-01-19T10:30:00"
}
```

### Trading Signals Endpoints

#### GET /signals/
Get trading signals based on subscription status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "signals": [
    {
      "symbol": "BTC/USDT",
      "action": "BUY",
      "entry_point": 45000.00,
      "stop_loss": 43500.00,
      "target": 47000.00,
      "confidence": 85
    }
  ],
  "total": 3,
  "is_paid": false,
  "cached": true,
  "message": "Showing 3 free signals. Upgrade to see all 20 signals."
}
```

**Free tier:** 3 signals  
**Paid tier:** 20 signals

### Billing Endpoints

#### POST /billing/create-checkout
Create Stripe checkout session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

#### GET /billing/status
Get subscription status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "is_paid": true,
  "stripe_customer_id": "cus_...",
  "stripe_subscription_id": "sub_..."
}
```

#### POST /billing/webhooks/stripe
Stripe webhook endpoint (called by Stripe, not authenticated).

**Headers:**
```
stripe-signature: <signature>
```

**Events Handled:**
- `checkout.session.completed`: Activates subscription

---

## 🔔 Stripe Webhook Setup

### 1. Install Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Windows (via Scoop)
scoop bucket add stripe https://github.com/stripe/scoop-stripe-cli.git
scoop install stripe

# Or download from: https://github.com/stripe/stripe-cli/releases
```

### 2. Login to Stripe

```bash
stripe login
```

### 3. Forward Webhooks (Development)

```bash
stripe listen --forward-to localhost:8000/billing/webhooks/stripe
```

This will output:
```
> Ready! Your webhook signing secret is whsec_xxxxx
```

Copy this secret to your `.env` file:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### 4. Test Webhook

```bash
stripe trigger checkout.session.completed
```

### 5. Production Webhook Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Set endpoint URL: `https://your-domain.com/billing/webhooks/stripe`
4. Select events to listen:
   - `checkout.session.completed`
5. Copy the **Signing secret**
6. Add to production `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_prod_xxxxx
```

### Webhook Testing with cURL

```bash
# Get your webhook secret from Stripe Dashboard
# Generate test signature (this is complex, use Stripe CLI instead)

# Or use Stripe CLI to trigger events:
stripe trigger checkout.session.completed \
  --override checkout.session.customer_email=test@example.com
```

### Verifying Webhooks Work

Check backend logs:
```bash
docker-compose logs -f backend
```

You should see:
```
Received Stripe webhook: checkout.session.completed (ID: evt_xxx)
Processing checkout.session.completed for session: cs_xxx
User 123 subscription activated successfully
```

---

## 👥 Authors

- Jinay Shah

---

**Last Updated:** January 19, 2026  
**Version:** 1.0.0  
