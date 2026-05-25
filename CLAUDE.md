# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
# Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env .env.local  # edit SECRET_KEY and DATABASE_URL as needed
```

`.env` must define `SECRET_KEY` (any string) and optionally `DATABASE_URL` (defaults to `sqlite:///./social.db`).

## Running the server

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` (Swagger) and `/redoc`.

The SQLite database (`social.db`) is created automatically on first startup via `Base.metadata.create_all()` in the lifespan handler.

## Architecture

This is a FastAPI REST API for a social/community mobile app. No test suite exists yet.

**Request flow:** Router → `dependencies.py` (auth/DB injection) → SQLAlchemy ORM → SQLite

**Key layers:**

- `app/core/config.py` — `Settings` singleton loaded from `.env` via pydantic-settings; imported everywhere as `settings`
- `app/core/security.py` — bcrypt password hashing (`passlib`) and JWT access/refresh token creation/decoding (`python-jose`); tokens carry `{"sub": user_id, "type": "access"|"refresh"}`
- `app/database.py` — SQLAlchemy engine, `SessionLocal`, and `Base` (DeclarativeBase)
- `app/dependencies.py` — `get_db()` (yields a DB session) and `get_current_user()` (extracts Bearer token → User); both used via `Depends()` in routers
- `app/models/` — ORM models; all must be imported via `app/models/__init__.py` so `Base.metadata` is populated before `create_all()` runs
- `app/schemas/` — Pydantic v2 request/response models, separate from ORM models
- `app/routers/` — one file per resource domain; each defines an `APIRouter` with a prefix

**Auth pattern:** Access tokens expire in 30 min; refresh tokens in 7 days. `POST /auth/refresh` accepts a refresh token and returns a new token pair. `get_current_user` only accepts access tokens (enforced by `token_type` check in `decode_token`).

**Feed logic** (`GET /posts`): returns posts from users the current user follows plus their own posts, ordered by `created_at` desc, with offset/limit pagination.

**Association tables:** `Follow` (follower_id, followed_id) and `Like` (user_id, post_id) use composite PKs — no surrogate ID column.

## Adding a new endpoint

1. Add/extend the ORM model in `app/models/` and import it in `app/models/__init__.py`
2. Add Pydantic schema in `app/schemas/`
3. Add route to the relevant router in `app/routers/`; use `Depends(get_current_user)` for authenticated routes
4. Register the router in `app/main.py` if it's new
