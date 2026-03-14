# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram Mini App wishlist service using Litestar (async Python web framework), PostgreSQL, and Telegram authentication. Users can create wishlists, send friend requests, and reserve gifts from friends' wishlists to avoid duplicate purchases.

## Key Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install all dependencies (dev + test groups)
uv sync --all-groups

# Set Python path for imports
export PYTHONPATH=$PYTHONPATH:$(pwd)/app

# Start Docker services (PostgreSQL + test database)
docker compose up --build -d
```

### Running the Application
```bash
# Start development server on http://localhost:80
python app/main.py

# API docs: http://localhost:80/schema/swagger
```

### Testing
```bash
# IMPORTANT: Start Docker containers before running integration tests
docker compose up -d

# Run all tests with coverage
uv run pytest -vv --cov=app --cov-report=html:htmlcov --cov-report=term

# Unit tests only (fast, no database)
uv run pytest -m unit -vv

# Integration tests only (use test database, requires Docker containers running)
uv run pytest -m integration -vv

# Run single test file
uv run pytest tests/unit_tests/user_domain_test.py -vv

# Run single test function
uv run pytest tests/integration_tests/services_test/user_test.py::TestUserService::test_service_get_user_success -vv
```

### Code Quality
```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run Ruff linter with auto-fix
ruff check --fix app tests

# Run Ruff formatter
ruff format app tests

# Run Ty type checker
ty check
```

### Database Migrations (Atlas)
```bash
# Create migration after modifying database_schema/schema.pg.hcl
atlas migrate diff {migration_name} --env local

# Apply pending migrations to local database
atlas migrate apply --env local

# Apply migrations to test database
atlas migrate apply --env local_test

# Check migration status
atlas migrate status --env local

# Rollback last migration
atlas migrate down --env local
```

## Architecture Overview

### Layered Architecture

The codebase follows a clean architecture pattern with strict separation of concerns:

```
Controllers → Services → Repositories → Database
     ↓           ↓            ↓
    DTOs      Domain       Raw SQL
```

**Key Principles:**
- **Controllers** (`app/controllers/`) handle HTTP requests/responses, perform validation, and call services
- **Services** (`app/services/`) contain business logic, orchestrate operations across repositories
- **Repositories** (`app/repositories/`) handle database access using raw SQL via SQLAlchemy's `session.execute()`
- **Domain** (`app/domain/`) contains domain models as dataclasses with business logic (e.g., `User`, `Gift`)
- **DTOs** (`app/dto/`) define request/response data transfer objects for API contracts

### Database Access Pattern

**IMPORTANT: This project does NOT use SQLAlchemy ORM**. All database access is raw SQL via `session.execute()`:

```python
# ✅ CORRECT - Raw SQL with text()
from sqlalchemy import text

stmt = text("SELECT * FROM users WHERE tg_id = :tg_id")
result = await self._session.execute(stmt, {'tg_id': tg_id})

# ❌ WRONG - No ORM models, no session.query()
# user = await session.query(User).filter_by(id=user_id).first()
```

All repositories inherit from `BaseRepository` which provides `self._session: AsyncSession`.

### Dependency Injection

Services are injected via Litestar's dependency system:

```python
# app/dependencies/provide_user_service.py
def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(db_session)

# app/controllers/users.py
@get('/me')
async def get_me(
    self,
    user_service: UserService,  # Auto-injected by Litestar
    current_user: int,  # From JWT token via provide_access_jwt_auth
) -> User:
    return await user_service.get(current_user)
```

Dependencies are defined in `app/dependencies/` and registered in controllers via `dependencies` parameter.

### Authentication Flow

1. Telegram Mini App sends `initData` to `POST /users/auth`
2. Backend validates `initData` signature using `TelegramAuth` (HMAC-SHA256)
3. User is created/updated in database via `UserService.telegram_login()`
4. JWT token generated with `user_id` claim via `BaseJWTAuth.create_token()`
5. Token returned to client, stored in localStorage
6. Protected endpoints use `provide_access_jwt_auth` dependency to extract `user_id` from token

**Key files:**
- `app/core/security/telegram_auth.py` - Telegram initData validation
- `app/core/security/jwt_auth.py` - JWT token creation/validation
- `app/dependencies/provide_access_jwt_auth.py` - Extracts user_id from token

### Domain Model Business Logic

Domain models (`app/domain/users.py`, `app/domain/gifts.py`) contain business logic:

```python
# User domain handles friend request logic
from domain.users import FriendAction

match user.resolve_friend_action(friend):
    case FriendAction.ALREADY_FRIENDS:
        raise BadRequestError(detail='Already friends')
    case FriendAction.ADD_FRIEND:
        await repository.accept_friend_request(sender_id, receiver_id)
    case FriendAction.SEND_REQUEST:
        await repository.send_friend_request(sender_id, receiver_id)
```

Services call domain methods for complex business rules, keeping services focused on orchestration.

### Testing Strategy

**Unit Tests** (`tests/unit_tests/`):
- Test domain logic, utilities, security functions
- No database interaction
- Use pytest-mock for mocking
- **Use hamcrest matchers for assertions**: When a test has multiple assertions, combine them using `assert_that()` with `all_of()` instead of multiple `assert` statements
  ```python
  # ✅ GOOD - Single assertion with hamcrest
  assert_that(user.avatar_url, all_of(equal_to(expected_url), has_length(200)))

  # ❌ BAD - Multiple assertions
  assert user.avatar_url == expected_url
  assert len(user.avatar_url) == 200
  ```
- **Use parametrize for similar tests**: When testing multiple similar cases, use `pytest.mark.parametrize()` with descriptive `id` parameter for each test case
  ```python
  # ✅ GOOD - Parametrized tests with descriptive ids
  @pytest.mark.parametrize(
      ('user_id', 'error_message'),
      [
          pytest.param(-1, 'User ID must be positive, got: -1', id='negative_user_id'),
          pytest.param(0, 'User ID must be positive, got: 0', id='zero_user_id'),
      ],
  )
  def test_validates_user_id(user_id: int, error_message: str) -> None:
      with pytest.raises(ValueError, match=error_message):
          User.create(user_id=user_id, ...)

  # ❌ BAD - Separate tests for similar cases
  def test_validates_negative_user_id() -> None:
      with pytest.raises(ValueError, match='User ID must be positive, got: -1'):
          User.create(user_id=-1, ...)

  def test_validates_zero_user_id() -> None:
      with pytest.raises(ValueError, match='User ID must be positive, got: 0'):
          User.create(user_id=0, ...)
  ```
- Example: `user_domain_test.py`, `jwt_auth_test.py`

**Integration Tests** (`tests/integration_tests/`):
- Test services and repositories with real test database
- Use transactional fixtures (rollback after each test)
- Fixtures create test data via raw SQL in `conftest.py`
- Example fixtures: `test_user_bob`, `test_user_with_friend`, `test_bob_gift_plane`

**Test Database Setup:**
- PostgreSQL test database: `{APP__DB__NAME}_test`
- Migrations applied via `atlas migrate apply --env local_test`
- Each test runs in a transaction that's rolled back (see `db_session` fixture in `conftest.py`)

### Logging

Uses `loguru` for structured logging:

```python
from loguru import logger

logger.info('User retrieved successfully: tg_id={}', tg_id)
logger.success('Friend request sent: sender={}, receiver={}', sender_id, receiver_id)
logger.error('Failed to create user with tg_id={}: {}', tg_id, type(e).__name__)
logger.warning('User tried to send friend request to themselves: tg_id={}', sender_id)
```

Logger configuration in `app/core/logger.py`. All services and repositories use structured logging for observability.

## Code Style & Conventions

### Ruff Configuration
- Line length: 120 characters
- Quote style: single quotes (`'string'`)
- Python version: 3.13+
- Import style: force single-line imports, sorted within sections
- Ignored rules defined in `pyproject.toml` (e.g., missing docstrings for all methods)

### Type Checking (Ty)
- Static type checker by Astral
- Extra paths: `app`, `tests`
- Ignore `possibly-missing-attribute` warnings
- Use `# ty:ignore[rule]` for specific suppressions

### Pre-commit Hooks
Automatically run on commit:
1. `pyupgrade` - Upgrade syntax to Python 3.13+
2. `ruff` - Linting + auto-fix
3. `ruff-format` - Code formatting
4. `ty` - Type checking
5. `export-requirements` - Update `requirements.txt` from `uv.lock` (no-dev dependencies only)

**Note:** The `requirements.txt` file is auto-generated from `uv.lock` and contains only production dependencies (no dev/test groups). Never edit it manually.

## Configuration Management

Settings loaded from environment variables via Pydantic Settings:

```python
# .env file structure
APP__DB__HOST=localhost
APP__DB__PORT=5432
APP__DB__NAME=wishlist
APP__DB__USER=postgres
APP__DB__PASSWORD=postgres
APP__BOT__TOKEN=your_telegram_bot_token
APP__JWT__SECRET_KEY=your_very_secret_key_min_32_chars_long
```

Access via `settings` singleton:
```python
from core.config import settings

settings.db.async_url  # Database connection URL
settings.jwt.secret_key  # JWT signing key
settings.bot.token  # Telegram bot token
```

Config classes in `app/core/config/`:
- `app.py` - App metadata
- `database.py` - Database settings
- `jwt.py` - JWT settings
- `bot.py` - Telegram bot settings
- `logger.py` - Logger settings
- `config.py` - Main Settings class

## Common Pitfalls

1. **Don't use SQLAlchemy ORM** - Use raw SQL with `text()` and `session.execute()`
2. **Set PYTHONPATH** - Required for imports to work: `export PYTHONPATH=$PYTHONPATH:$(pwd)/app`
3. **Start Docker containers before integration tests** - Run `docker compose up -d` before running integration tests
4. **Apply migrations to both databases** - Run `atlas migrate apply` for both `local` and `local_test` envs
5. **Don't commit without pre-commit** - `requirements.txt` must be updated automatically
6. **Coverage omits certain files** - Controllers, DTOs, config, and entrypoints excluded from coverage (see `pyproject.toml`)
7. **Tests must be marked** - Use `@pytest.mark.unit` or `@pytest.mark.integration` markers
8. **AsyncSession in repos** - All repository methods must be `async` and use `await session.execute()`
9. **Bidirectional friendships** - Friend relationships insert two rows (both directions) in `friends` table

## Database Schema Notes

**Important constraints:**
- `users.tg_id` is the primary key (bigint from Telegram)
- `friends` table has bidirectional rows: if A friends B, both (A,B) and (B,A) exist
- `friend_requests.status` is enum: `pending`, `accepted`, `rejected`
- `gift_reservations.gift_id` is primary key (one-to-one with gifts)
- All foreign keys use `CASCADE` on delete

**Schema source of truth:** `database_schema/schema.pg.hcl` (Atlas HCL format)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):
1. Pre-commit checks (linting, formatting, type checking)
2. Run full test suite with coverage
3. Upload coverage to Coveralls

Badge in README shows build status and coverage percentage.
