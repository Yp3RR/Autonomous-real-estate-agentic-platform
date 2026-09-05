import sqlite3
import json
from typing import List

DB_PATH = "sessions.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            parts TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def get_history(session_id: str) -> List[dict]:
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT role, parts FROM sessions WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "parts": json.loads(row[1])} for row in rows]


def add_message(session_id: str, role: str, text: str):
    conn = _get_connection()
    conn.execute(
        "INSERT INTO sessions (session_id, role, parts) VALUES (?, ?, ?)",
        (session_id, role, json.dumps([text]))
    )
    conn.commit()
    conn.close()


def clear_session(session_id: str):
    conn = _get_connection()
    conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def session_exists(session_id: str) -> bool:
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1",
        (session_id,)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists