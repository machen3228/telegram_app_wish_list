# 🎁 Telegram Wishlist App

[![CI](https://github.com/machen3228/telegram_app_wish_list/actions/workflows/ci.yml/badge.svg)](https://github.com/machen3228/telegram_app_wish_list/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/machen3228/telegram_app_wish_list/badge.svg?branch=main)](https://coveralls.io/github/machen3228/telegram_app_wish_list?branch=main)

A Telegram Mini App that simplifies gift selection for any occasion. Share your wishlist with friends, see what they want, and coordinate gift purchases to avoid duplicates.

**Try it now:** [@wishlist_pretty_bot](https://t.me/wishlist_pretty_bot)

## 🌟 Features

- **Personal Wishlists** — Add gifts with details: name, link, price, priority (1-10 scale), and personal notes
- **Gift Reservations** — Reserve friends' gifts to prevent duplicate purchases and coordinate who's buying what
- **Friend Management** — Send/accept/reject friend requests with bidirectional relationships
- **Private Wishlists** — Only friends can view your complete wishlist; others see basic profile info
- **Telegram Integration** — Seamless login via Telegram Mini App using `telegram-web-app.js`
- **Reservation History** — Track which gifts you've reserved from your friends

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          Telegram Mini App (React Frontend)                 │
│  github.com/machen3228/telegram_frontend_wish_list          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    Litestar Backend                         │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │ Controllers│  │  Services  │  │  JWT Authentication │    │
│  └────────────┘  └────────────┘  └─────────────────────┘    │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │Repositories│  │   Domain   │  │ Telegram Auth Data  │    │
│  └────────────┘  └────────────┘  └─────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL Queries (asyncpg)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                            │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │   Users    │  │   Gifts    │  │ Gift Reservations   │    │
│  └────────────┘  └────────────┘  └─────────────────────┘    │
│  ┌────────────┐  ┌────────────┐                             │
│  │  Friends   │  │Friend Reqs │                             │
│  └────────────┘  └────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Tech Stack

### Backend
- **Framework**: [Litestar](https://docs.litestar.dev/) 2.21+ — async Python web framework
- **Database**: PostgreSQL 15+ with async support via asyncpg
- **ORM/Query**: SQLAlchemy 2.0+ (raw SQL via `session.execute()`, no ORM layer)
- **Authentication**: JWT (PyJWT) + Telegram Mini App authentication
- **Async Runtime**: uvicorn + asyncio
- **Migrations**: [Atlas](https://atlasgo.sh/) (HCL-based migration tool)

### Development & Quality
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (fast Python package manager by Astral)
- **Linter/Formatter**: [Ruff](https://docs.astral.sh/ruff/) (all-in-one Python linter + formatter by Astral)
- **Type Checker**: [Ty](https://docs.astral.sh/ty/) (static type checker by Astral)
- **Testing**: pytest + pytest-asyncio + pytest-cov + pyhamcrest
- **Coverage**: Coveralls integration with GitHub Actions

### DevOps
- **Containerization**: Docker Compose (local development)
- **CI/CD**: GitHub Actions (code quality checks, tests, coverage reporting)

### Frontend
- **React** — Separate repository: [telegram_frontend_wish_list](https://github.com/machen3228/telegram_frontend_wish_list)
- **Telegram Web App SDK**: `telegram-web-app.js`

## 📊 Database Schema

### Tables Overview

```
users
├── tg_id (PK, bigint) — Telegram user ID
├── tg_username (unique, varchar)
├── first_name, last_name (varchar)
├── avatar_url (varchar)
└── timestamps (created_at, updated_at)

gifts
├── id (PK, bigserial)
├── user_id (FK → users.tg_id, CASCADE)
├── name (varchar, required)
├── url (varchar, optional)
├── wish_rate (smallint, 1-10 priority scale)
├── price (numeric, optional)
├── note (text, optional)
└── timestamps (created_at, updated_at)

friends (bidirectional relationship)
├── user_tg_id (FK → users, CASCADE)
├── friend_tg_id (FK → users, CASCADE)
├── PK: (user_tg_id, friend_tg_id)
└── CHECK: no self-friendships

friend_requests (with status tracking)
├── sender_tg_id (FK → users, CASCADE)
├── receiver_tg_id (FK → users, CASCADE)
├── status (pending/accepted/rejected)
├── timestamps (created_at, updated_at)
└── Indices: on receiver_id and status

gift_reservations (one-to-one with gifts)
├── gift_id (PK, FK → gifts, CASCADE)
├── reserved_by_tg_id (FK → users, CASCADE)
└── created_at
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **Docker & Docker Compose**
- **Git**

### Installation

1. **Install uv package manager:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Create and activate virtual environment:**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install all dependencies (including dev & test groups):**
```bash
uv sync --all-groups
```

4. **Start Docker services (PostgreSQL, test database):**
```bash
docker compose up --build -d
```

5. **Set Python path (for imports):**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/app
```

6. **Run the application:**
```bash
python app/main.py
```

The app will start on `http://localhost:80`

**View API documentation:** Open http://localhost:80/schema/swagger in your browser

### Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
# Database
APP__DB__HOST=localhost
APP__DB__PORT=5432
APP__DB__NAME=wishlist
APP__DB__USER=postgres
APP__DB__PASSWORD=postgres

# Telegram Bot Token (for future bot features)
APP__BOT__TOKEN=your_telegram_bot_token

# JWT Secret (min 32 characters)
APP__JWT__SECRET_KEY=your_very_secret_key_min_32_chars_long

# Docker volumes
VOLUMES_DIR=~/projects/telegram_app_wish_list
```

## 🗄️ Database Migrations

This project uses **Atlas** for database version control. Atlas files are stored in `/database_schema/schema.pg.hcl`.

### Install Atlas

```bash
curl -sSf https://atlasgo.sh | sh
```

### Common Migration Commands

**Create a new migration** (after modifying `schema.pg.hcl`):
```bash
atlas migrate diff {migration_name} --env local
```

**Apply pending migrations** to local database:
```bash
atlas migrate apply --env local
atlas migrate apply --env local_test # for test db migrations
```

**Check migration status:**
```bash
atlas migrate status --env local
```

**Rollback the last migration:**
```bash
atlas migrate down --env local
```

> **Tip**: Install the Atlas plugin in your IDE (PyCharm, VS Code) for syntax highlighting on `.pg.hcl` files.

## 🧪 Testing

The project has two types of tests:

### Unit Tests
Fast, no database interaction. Location: `tests/unit_tests/`
```bash
uv run -m unit -vv
```

### Integration Tests
Use the test database. Location: `tests/integration_tests/`
```bash
uv run -m integration -vv
```

### Run All Tests with Coverage
```bash
uv run pytest -vv --cov=app --cov-report=html:htmlcov --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`


## 📡 API Endpoints

### Authentication
- `POST /users/auth` — Login via Telegram Mini App (returns JWT token)

### Users
- `GET /users/me` — Get current user profile
- `GET /users/{tg_id}` — Get user by Telegram ID
- `GET /users/me/friends` — List all friends with details
- `POST /users/me/friends/{receiver_id}/request` — Send friend request
- `GET /users/me/friend-requests` — Get pending friend requests
- `PATCH /users/me/friends/{sender_id}/accept` — Accept friend request
- `PATCH /users/me/friends/{sender_id}/reject` — Reject friend request
- `DELETE /users/me/friends/{friend_id}/delete` — Remove friend (bidirectional)

### Gifts
- `POST /gifts` — Add gift to wishlist (requires auth)
- `GET /gifts/user/{tg_id}` — View user's wishlist (friends only)
- `DELETE /gifts/{gift_id}` — Delete your gift (requires auth)
- `POST /gifts/{gift_id}/reserve` — Reserve a friend's gift (requires auth)
- `DELETE /gifts/{gift_id}/reserve` — Cancel reservation (requires auth)
- `GET /gifts/my/reserve` — Get all gifts you've reserved (requires auth)

All endpoints except `/users/{tg_id}` require JWT authentication via the `Authorization: Bearer {token}` header.

## 🏢 Project Structure

```
app/
├── controllers/           # HTTP request handlers
│   ├── gifts.py
│   └── users.py
├── services/             # Business logic
│   ├── gifts.py
│   └── users.py
├── repositories/         # Database access layer
│   ├── base.py
│   ├── gifts.py
│   └── users.py
├── domain/              # Domain models (dataclasses)
│   ├── gifts.py
│   └── users.py
├── dto/                 # Data Transfer Objects
│   ├── gifts.py
│   └── users.py
├── core/
│   ├── config/          # Configuration management
│   ├── security/        # JWT & Telegram auth
│   └── database/        # SQLAlchemy setup
├── dependencies/        # Dependency injection providers
├── exceptions/          # Custom exceptions
├── utils/               # Utilities
├── main.py              # App entry point
└── application.py       # Litestar app setup

tests/
├── unit_tests/          # Fast tests (no DB)
└── integration_tests/   # Full integration tests
```

## 🔐 Authentication Flow

1. **Telegram Mini App opens** with `initData` query parameter
2. **Frontend** calls `POST /users/auth` with `initData`
3. **Backend** validates `initData` signature using Telegram Bot token
4. **JWT token created** with `user_id` claim
5. **Token stored** in frontend localStorage
6. **Subsequent requests** include `Authorization: Bearer {token}` header

Access tokens are validated using the symmetric key stored in `APP__JWT__SECRET_KEY`.

## 🔍 Code Quality

This project uses automated code quality checks:

### Pre-commit Hooks
```bash
uv tool install pre-commit
pre-commit run --all-files
```

Checks include:
- **Ruff linting** (code style, imports, complexity)
- **Ruff formatting** (code formatting to single quotes, 120 char lines)
- **Ty type checking** (static type analysis)

### GitHub Actions CI
Every push/PR runs:
1. Pre-commit checks (linting, formatting, type checking)
2. Full test suite with coverage
3. Coverage report to Coveralls

See `.github/workflows/ci.yml` for details.

## 📝 Development Workflow

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes** and ensure tests pass:
```bash
uv run pytest
```

3. **Run pre-commit checks:**
```bash
pre-commit run --all-files
```

4. **Commit and push:**
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/your-feature-name
```

5. **Create a Pull Request** — CI will automatically check code quality and tests

## 🔮 Future Plans

- **Deployment** — Set up production deployment (likely to Railway or similar platform)
- **Push Notifications** — Notify friends when their wishlist is updated
- **Search & Filters** — Advanced wishlist filtering by category, price, priority
- **Wishlist Categories** — Organize gifts by occasion (birthday, wedding, etc.)

## 📄 License

This project is open source. See LICENSE file for details.

## 👨‍💻 Author

**machen3228** — [GitHub](https://github.com/machen3228)

---

**Have questions or want to contribute?** Feel free to open an issue or PR! 🚀
