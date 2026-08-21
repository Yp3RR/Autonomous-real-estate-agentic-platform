from typing import Dict, List

_sessions: Dict[str, List[dict]] = {}


def get_history(session_id: str) -> List[dict]:
    return _sessions.get(session_id, [])


def add_message(session_id: str, role: str, text: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({
        "role": role,
        "parts": [text]
    })


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]


def session_exists(session_id: str) -> bool:
    return session_id in _sessions