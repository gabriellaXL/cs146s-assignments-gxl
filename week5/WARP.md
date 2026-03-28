# Warp Project Rules — week5

## Scope
All changes must stay within `week5/`. Do not modify other weeks' directories unless explicitly instructed and justified.

## Tech Stack
- **Backend**: FastAPI + SQLite, SQLAlchemy 2.x ORM, Pydantic v2
- **Frontend**: Static HTML + vanilla JS in `frontend/`
- **Tests**: pytest in `backend/tests/`, using a temporary SQLite DB (see `conftest.py`)
- **Formatting**: `black` (line-length 100) + `ruff`
- **All `make` commands run from the `week5/` directory**

## Project Structure
```
backend/app/
  main.py          # FastAPI app entry point, static mount, startup event
  models.py        # SQLAlchemy ORM models
  schemas.py       # Pydantic v2 request/response schemas
  db.py            # Engine, session factory, get_db dependency, seed logic
  routers/
    notes.py       # /notes endpoints
    action_items.py # /action-items endpoints
  services/
    extract.py     # Text extraction logic (non-route business logic)
backend/tests/     # pytest test files
frontend/          # Static assets served at /static; index.html served at /
data/
  seed.sql         # Seed run once on fresh DB creation
  app.db           # SQLite database (gitignored)
docs/              # Documentation (API.md, TASKS.md, etc.)
```

## Development Conventions
- Schema changes (request/response shapes) → `backend/app/schemas.py`
- ORM model changes (tables, columns) → `backend/app/models.py`; also update `data/seed.sql`
- New routes → add a file in `backend/app/routers/` and include it in `main.py`
- Business logic that is not routing → `backend/app/services/`
- Always add or update tests in `backend/tests/` alongside every code change
- Tests must use the `client` fixture from `conftest.py` (isolates a fresh DB per test)

## Before Declaring Any Task Complete
1. `make format` — auto-fix formatting with black + ruff
2. `make lint` — catch remaining lint issues (must pass clean)
3. `make test` — all tests must pass
4. If API endpoints were added or changed → update `docs/API.md`
5. Do not commit with failing tests or lint errors

## Running the App
```bash
# From week5/
make run          # starts uvicorn on http://localhost:8000
make test         # runs pytest
make format       # black + ruff --fix
make lint         # ruff check only
```

## Database Notes
- Default DB path: `data/app.db` (override with `DATABASE_PATH` env var)
- Tests use an isolated temporary DB — never touch `data/app.db` in tests
- Seed is applied automatically on first run when DB file does not exist
