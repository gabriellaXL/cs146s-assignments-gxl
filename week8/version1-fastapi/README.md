# Version 1: FastAPI Notes Manager

This project is the FastAPI implementation of the Week 8 multi-stack assignment. It provides the same note-focused CRUD app as the other versions, using a Python API backend, SQLite persistence, and a lightweight static frontend.

## Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Vanilla HTML/CSS/JavaScript frontend

## Features

- Create notes with title, content, and status
- Browse all notes in a list with search and sort
- View note details
- Edit notes
- Delete notes with confirmation
- Persist data in SQLite
- Validate title/content length and status values

## Project Structure

```text
week8/version1-fastapi/
  backend/app/             FastAPI app, models, schemas, and note router
  backend/tests/           API tests
  frontend/                Static frontend served by FastAPI
  data/                    SQLite database location
  README.md
```

## Setup

1. Install dependencies from the repository root:

```powershell
poetry install
```

2. Move into this project:

```powershell
cd week8/version1-fastapi
```

3. (Optional) copy the environment template:

```powershell
Copy-Item .env.example .env
```

4. Start the app:

```powershell
poetry run uvicorn backend.app.main:app --reload
```

5. Open:

- `http://127.0.0.1:8000/` for the frontend
- `http://127.0.0.1:8000/docs` for API docs

## Configuration

- Default SQLite path: `./data/app.db`
- Override with `DATABASE_PATH` in `.env`

## Tests

Run from `week8/version1-fastapi`:

```powershell
poetry run pytest -q backend/tests
```

## Manual Notes

- This version intentionally keeps the frontend minimal and server-served, so the stack stays distinct from both Django templates and the Bolt-generated React app.
- The app is intentionally scoped to a single primary resource (`Note`) to keep week8 functionality consistent across all three implementations.
