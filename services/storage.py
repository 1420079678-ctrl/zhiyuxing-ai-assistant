from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def database_path() -> Path:
    configured = os.getenv("CHAT_DB_PATH", "").strip()
    if configured:
        return Path(configured)
    return BASE_DIR / "data" / "zhiyuxing.db"


def ensure_database() -> None:
    db_path = database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                response_style TEXT,
                provider_name TEXT,
                model_name TEXT,
                mode TEXT,
                risk_level TEXT,
                knowledge_sources TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                assistant_message_id INTEGER NOT NULL,
                rating TEXT NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def connect() -> sqlite3.Connection:
    ensure_database()
    connection = sqlite3.connect(database_path())
    connection.row_factory = sqlite3.Row
    return connection


def ensure_session(session_id: str | None, first_message: str | None = None) -> str:
    resolved_session_id = (session_id or "").strip() or f"sess_{uuid.uuid4().hex[:12]}"
    now = utc_now()
    title = (first_message or "").strip()[:60] or "新会话"

    with connect() as connection:
        exists = connection.execute(
            "SELECT 1 FROM sessions WHERE session_id = ?",
            (resolved_session_id,),
        ).fetchone()
        if exists:
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (now, resolved_session_id),
            )
        else:
            connection.execute(
                "INSERT INTO sessions (session_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (resolved_session_id, title, now, now),
            )

    return resolved_session_id


def save_message(
    session_id: str,
    role: str,
    content: str,
    *,
    response_style: str | None = None,
    provider_name: str | None = None,
    model_name: str | None = None,
    mode: str | None = None,
    risk_level: str | None = None,
    knowledge_sources: list[str] | None = None,
) -> int:
    now = utc_now()
    sources_payload = json.dumps(knowledge_sources or [], ensure_ascii=False)
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages (
                session_id, role, content, response_style, provider_name,
                model_name, mode, risk_level, knowledge_sources, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                response_style,
                provider_name,
                model_name,
                mode,
                risk_level,
                sources_payload,
                now,
            ),
        )
        connection.execute(
            "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
            (now, session_id),
        )
        return int(cursor.lastrowid)


def save_turn(
    session_id: str,
    user_message: str,
    assistant_message: str,
    *,
    response_style: str,
    provider_name: str,
    model_name: str,
    mode: str,
    risk_level: str,
    knowledge_sources: list[str],
) -> int:
    save_message(session_id, "user", user_message, mode=mode, risk_level=risk_level)
    return save_message(
        session_id,
        "assistant",
        assistant_message,
        response_style=response_style,
        provider_name=provider_name,
        model_name=model_name,
        mode=mode,
        risk_level=risk_level,
        knowledge_sources=knowledge_sources,
    )


def recent_messages(session_id: str, limit: int = 6) -> list[dict[str, str]]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()

    ordered_rows = list(reversed(rows))
    return [{"role": row["role"], "content": row["content"]} for row in ordered_rows]


def session_history(session_id: str, limit: int = 20) -> dict[str, Any]:
    with connect() as connection:
        session = connection.execute(
            "SELECT session_id, title, created_at, updated_at FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        rows = connection.execute(
            """
            SELECT id, role, content, provider_name, model_name, mode, risk_level, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        total_messages = connection.execute(
            "SELECT COUNT(*) AS total FROM messages WHERE session_id = ?",
            (session_id,),
        ).fetchone()["total"]

    messages = [
        {
            "id": int(row["id"]),
            "role": row["role"],
            "content": row["content"],
            "provider_name": row["provider_name"],
            "model_name": row["model_name"],
            "mode": row["mode"],
            "risk_level": row["risk_level"],
            "created_at": row["created_at"],
        }
        for row in reversed(rows)
    ]

    return {
        "session_id": session_id,
        "title": session["title"] if session else None,
        "created_at": session["created_at"] if session else None,
        "updated_at": session["updated_at"] if session else None,
        "total_messages": int(total_messages or 0),
        "messages": messages,
    }


def save_feedback(session_id: str, assistant_message_id: int, rating: str, comment: str | None = None) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO feedback (session_id, assistant_message_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, assistant_message_id, rating, comment, utc_now()),
        )
