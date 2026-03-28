from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


# AI-generated (TODO3): database-layer exception boundary for consistent API error mapping.
class DatabaseError(Exception):
    """Raised when database operations fail."""


def ensure_data_directory_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    # AI-generated (TODO3): normalize connection setup (row_factory + FK enforcement).
    try:
        ensure_data_directory_exists()
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        # Make foreign keys explicit and deterministic.
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    except sqlite3.Error as exc:
        raise DatabaseError("failed to open database connection") from exc


def init_db() -> None:
    # AI-generated (TODO3): startup-safe schema initialization with wrapped DB errors.
    try:
        ensure_data_directory_exists()
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            connection.commit()
    except sqlite3.Error as exc:
        raise DatabaseError("failed to initialize database") from exc


def insert_note(content: str) -> int:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise DatabaseError("failed to insert note") from exc


def list_notes() -> list[sqlite3.Row]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            return list(cursor.fetchall())
    except sqlite3.Error as exc:
        raise DatabaseError("failed to list notes") from exc


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            return row
    except sqlite3.Error as exc:
        raise DatabaseError("failed to fetch note") from exc


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            connection.commit()
            return ids
    except sqlite3.Error as exc:
        raise DatabaseError("failed to insert action items") from exc


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            return list(cursor.fetchall())
    except sqlite3.Error as exc:
        raise DatabaseError("failed to list action items") from exc


def mark_action_item_done(action_item_id: int, done: bool) -> bool:
    # AI-generated (TODO3): return update status so router can emit proper 404 semantics.
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            connection.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise DatabaseError("failed to update action item status") from exc
