# Version 3: Django Notes Manager

This project is the Django implementation of the Week 8 multi-stack assignment. It provides a stable, server-rendered notes manager with full CRUD, SQLite persistence, validation, and basic automated tests.

## Stack

- Python 3.10+
- Django
- SQLite

## Features

- Create, list, view, update, and delete notes
- SQLite-backed persistence
- Server-rendered HTML pages using Django templates
- Form validation with user-facing error messages
- Timestamps and note status tracking
- Basic Django test coverage for core flows

## Project Structure

```text
week8/version3-django/
├── config/                 Django project settings and root URLs
├── notes/                  Notes app with models, forms, views, and tests
├── templates/              Shared and app templates
├── manage.py
└── README.md
```

## Setup

1. Install dependencies from the repository root:

```powershell
poetry install
```

2. Move into the Django project directory:

```powershell
cd week8/version3-django
```

3. Apply database migrations:

```powershell
poetry run python manage.py migrate
```

4. Start the development server:

```powershell
poetry run python manage.py runserver
```

4. Open `http://127.0.0.1:8000/notes/`

## Tests

Run the Django test suite:

```powershell
cd week8/version3-django
poetry run python manage.py test
```

## Persistence

The project uses SQLite. The development database is stored at:

`week8/version3-django/db.sqlite3`

## Manual Notes

- This version intentionally uses Django templates instead of a separate frontend to keep the stack fully non-JavaScript on the application side.
- The app focuses on the primary `Note` resource to keep the scope aligned across all three Week 8 implementations.
