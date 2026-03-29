import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "./data/app.db")

engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


def apply_schema_updates() -> None:
    with engine.begin() as conn:
        inspector = inspect(conn)
        tables = set(inspector.get_table_names())
        if "action_items" not in tables:
            return

        columns = {column["name"] for column in inspector.get_columns("action_items")}
        if "project_id" not in columns:
            conn.execute(text("ALTER TABLE action_items ADD COLUMN project_id INTEGER"))

        conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_action_items_project_id ON action_items(project_id)")
        )


def apply_seed_if_needed() -> None:
    db_path = Path(DEFAULT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        db_path.touch()

    seed_file = Path("./data/seed.sql")
    if not seed_file.exists():
        return

    with engine.begin() as conn:
        if not _seed_required(conn):
            return

        sql = seed_file.read_text()
        if sql.strip():
            for statement in [s.strip() for s in sql.split(";") if s.strip()]:
                conn.execute(text(statement))


def _seed_required(conn: Session) -> bool:
    tables_to_check = ("notes", "action_items", "projects")
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())
    for table_name in tables_to_check:
        if table_name not in existing_tables:
            return False
        row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
        if row_count > 0:
            return False
    return True
