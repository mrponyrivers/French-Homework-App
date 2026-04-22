from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path("french_homework.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS vocab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            meaning TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        )
    """)

    cols = [row["name"] for row in conn.execute("PRAGMA table_info(vocab)").fetchall()]

    if "meaning" not in cols:
        conn.execute("ALTER TABLE vocab ADD COLUMN meaning TEXT")

    if "notes" not in cols:
        conn.execute("ALTER TABLE vocab ADD COLUMN notes TEXT")

    conn.commit()


def insert_lesson(conn: sqlite3.Connection, title: str, content: str) -> int:
    cursor = conn.execute("""
        INSERT INTO lessons (title, content)
        VALUES (?, ?)
    """, (title.strip(), content))
    conn.commit()
    return cursor.lastrowid


def get_lessons(conn: sqlite3.Connection):
    rows = conn.execute("""
        SELECT id, title, content, created_at
        FROM lessons
        ORDER BY created_at DESC, id DESC
    """).fetchall()

    return [dict(row) for row in rows]


def get_lesson_by_id(conn: sqlite3.Connection, lesson_id: int):
    row = conn.execute("""
        SELECT id, title, content, created_at
        FROM lessons
        WHERE id = ?
    """, (lesson_id,)).fetchone()

    return dict(row) if row else None


def delete_vocab_for_lesson(conn: sqlite3.Connection, lesson_id: int) -> None:
    conn.execute("""
        DELETE FROM vocab
        WHERE lesson_id = ?
    """, (lesson_id,))
    conn.commit()


def insert_vocab_item(
    conn: sqlite3.Connection,
    lesson_id: int,
    term: str,
    meaning: str,
    notes: str = ""
) -> None:
    conn.execute("""
        INSERT INTO vocab (lesson_id, term, meaning, notes)
        VALUES (?, ?, ?, ?)
    """, (
        lesson_id,
        term.strip(),
        meaning.strip(),
        notes.strip(),
    ))
    conn.commit()


def insert_vocab_items_bulk(
    conn: sqlite3.Connection,
    lesson_id: int,
    items: list[dict]
) -> None:
    cleaned_rows = []
    for item in items:
        term = (item.get("term") or "").strip()
        meaning = (item.get("meaning") or "").strip()
        notes = (item.get("notes") or "").strip()

        if not term:
            continue

        cleaned_rows.append((lesson_id, term, meaning, notes))

    if not cleaned_rows:
        return

    conn.executemany("""
        INSERT INTO vocab (lesson_id, term, meaning, notes)
        VALUES (?, ?, ?, ?)
    """, cleaned_rows)
    conn.commit()


def get_vocab_for_lesson(conn: sqlite3.Connection, lesson_id: int):
    rows = conn.execute("""
        SELECT id, lesson_id, term, meaning, notes, created_at
        FROM vocab
        WHERE lesson_id = ?
        ORDER BY term COLLATE NOCASE ASC, id ASC
    """, (lesson_id,)).fetchall()

    return [dict(row) for row in rows]


def get_quiz_ready_vocab_for_lesson(conn: sqlite3.Connection, lesson_id: int):
    rows = conn.execute("""
        SELECT id, lesson_id, term, meaning, notes, created_at
        FROM vocab
        WHERE lesson_id = ?
          AND term IS NOT NULL
          AND TRIM(term) != ''
          AND meaning IS NOT NULL
          AND TRIM(meaning) != ''
        ORDER BY term COLLATE NOCASE ASC, id ASC
    """, (lesson_id,)).fetchall()

    return [dict(row) for row in rows]