from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Any


DB_PATH = Path("data/app.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_names(conn: sqlite3.Connection, table_name: str) -> set[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    rows = cur.fetchall()
    return {row["name"] for row in rows}


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lessons (
            lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            raw_text TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            exercise_title TEXT NOT NULL,
            exercise_text TEXT NOT NULL,
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vocab_items (
            vocab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT '',
            meaning TEXT,
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_tables (
            table_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            table_number INTEGER NOT NULL,
            table_json TEXT NOT NULL,
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id)
        )
        """
    )

    vocab_columns = _column_names(conn, "vocab_items")
    if "meaning" not in vocab_columns:
        cur.execute("ALTER TABLE vocab_items ADD COLUMN meaning TEXT")

    conn.commit()
    conn.close()


def save_lesson(filename: str, uploaded_at: str, raw_text: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO lessons (filename, uploaded_at, raw_text)
        VALUES (?, ?, ?)
        """,
        (filename, uploaded_at, raw_text),
    )

    lesson_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(lesson_id)


def save_exercises(lesson_id: int, exercises: list[dict[str, Any]]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    rows = [
        (
            lesson_id,
            str(exercise.get("title", "")).strip(),
            str(exercise.get("text", "")).strip(),
        )
        for exercise in exercises
        if str(exercise.get("title", "")).strip() or str(exercise.get("text", "")).strip()
    ]

    if rows:
        cur.executemany(
            """
            INSERT INTO exercises (lesson_id, exercise_title, exercise_text)
            VALUES (?, ?, ?)
            """,
            rows,
        )

    conn.commit()
    conn.close()


def save_vocab_items(lesson_id: int, vocab_items: list[dict[str, str]]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cleaned_rows = []
    seen_terms = set()

    for item in vocab_items:
        term = str(item.get("term", "")).strip()
        meaning = str(item.get("meaning", "")).strip()

        if not term:
            continue

        normalized_term = " ".join(term.lower().split())
        if normalized_term in seen_terms:
            continue
        seen_terms.add(normalized_term)

        cleaned_rows.append((lesson_id, term, "", meaning))

    if cleaned_rows:
        cur.executemany(
            """
            INSERT INTO vocab_items (lesson_id, term, source_type, meaning)
            VALUES (?, ?, ?, ?)
            """,
            cleaned_rows,
        )

    conn.commit()
    conn.close()


def save_lesson_tables(lesson_id: int, tables: list[dict[str, Any]]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    rows = [
        (
            lesson_id,
            table["table_number"],
            json.dumps(table["rows"], ensure_ascii=False),
        )
        for table in tables
    ]

    if rows:
        cur.executemany(
            """
            INSERT INTO lesson_tables (lesson_id, table_number, table_json)
            VALUES (?, ?, ?)
            """,
            rows,
        )

    conn.commit()
    conn.close()


def get_lessons() -> list[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT lesson_id, filename, uploaded_at
        FROM lessons
        ORDER BY lesson_id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_lesson_with_exercises(lesson_id: int) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT lesson_id, filename, uploaded_at, raw_text
        FROM lessons
        WHERE lesson_id = ?
        """,
        (lesson_id,),
    )
    lesson = cur.fetchone()

    cur.execute(
        """
        SELECT exercise_id, exercise_title, exercise_text
        FROM exercises
        WHERE lesson_id = ?
        ORDER BY exercise_id ASC
        """,
        (lesson_id,),
    )
    exercises = cur.fetchall()

    conn.close()
    return lesson, exercises


def get_vocab_for_lesson(lesson_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT vocab_id, term, meaning
        FROM vocab_items
        WHERE lesson_id = ?
        ORDER BY term COLLATE NOCASE ASC
        """,
        (lesson_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_tables_for_lesson(lesson_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT table_number, table_json
        FROM lesson_tables
        WHERE lesson_id = ?
        ORDER BY table_number ASC
        """,
        (lesson_id,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "table_number": row["table_number"],
            "rows": json.loads(row["table_json"]),
        }
        for row in rows
    ]


def delete_lesson(lesson_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM exercises WHERE lesson_id = ?", (lesson_id,))
    cur.execute("DELETE FROM vocab_items WHERE lesson_id = ?", (lesson_id,))
    cur.execute("DELETE FROM lesson_tables WHERE lesson_id = ?", (lesson_id,))
    cur.execute("DELETE FROM lessons WHERE lesson_id = ?", (lesson_id,))

    conn.commit()
    conn.close()


def get_recent_lesson_ids(limit: int = 2) -> list[int]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT lesson_id
        FROM lessons
        ORDER BY lesson_id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    return [int(row["lesson_id"]) for row in rows]


def delete_last_lessons(limit: int = 2) -> list[int]:
    lesson_ids = get_recent_lesson_ids(limit=limit)
    for lesson_id in lesson_ids:
        delete_lesson(lesson_id)
    return lesson_ids