import json
from typing import List
from backend.database import get_connection


def get_history(session_id: str) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, parts FROM sessions WHERE session_id = %s ORDER BY created_at",
        (session_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": row["role"], "parts": json.loads(row["parts"])} for row in rows]


def add_message(session_id: str, role: str, text: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (session_id, role, parts) VALUES (%s, %s, %s)",
        (session_id, role, json.dumps([text]))
    )
    conn.commit()
    cur.close()
    conn.close()


def clear_session(session_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
    conn.commit()
    cur.close()
    conn.close()


def session_exists(session_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM sessions WHERE session_id = %s LIMIT 1",
        (session_id,)
    )
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists