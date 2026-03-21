import sqlite3

from services.storage import connect, database_path, ensure_database, ensure_session, recent_messages, save_feedback, save_turn, session_history


def test_ensure_database_creates_sqlite_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "storage-test.db"))

    ensure_database()

    assert database_path().exists()


def test_ensure_session_creates_and_updates_session(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "session-test.db"))

    session_id = ensure_session(None, "第一次消息")
    same_session_id = ensure_session(session_id, "第二次消息")

    assert session_id == same_session_id
    assert session_id.startswith("sess_")


def test_save_turn_and_recent_messages(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "turn-test.db"))
    session_id = ensure_session(None, "最近好吗")

    assistant_message_id = save_turn(
        session_id,
        "最近好吗",
        "可以先从今天最小的一步开始。",
        response_style="balanced",
        provider_name="Local Demo",
        model_name="builtin-demo",
        mode="demo",
        risk_level="low",
        knowledge_sources=["测试知识"],
    )
    messages = recent_messages(session_id, limit=5)

    assert assistant_message_id > 0
    assert messages == [
        {"role": "user", "content": "最近好吗"},
        {"role": "assistant", "content": "可以先从今天最小的一步开始。"},
    ]


def test_session_history_returns_saved_messages(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "history-test.db"))
    session_id = ensure_session(None, "第一轮")
    save_turn(
        session_id,
        "第一轮",
        "第一条回复",
        response_style="balanced",
        provider_name="Local Demo",
        model_name="builtin-demo",
        mode="demo",
        risk_level="low",
        knowledge_sources=[],
    )

    payload = session_history(session_id)

    assert payload["session_id"] == session_id
    assert payload["total_messages"] == 2
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][1]["role"] == "assistant"


def test_save_feedback_persists_record(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "feedback-test.db"))
    session_id = ensure_session(None, "反馈会话")
    assistant_message_id = save_turn(
        session_id,
        "反馈会话",
        "回复内容",
        response_style="balanced",
        provider_name="Local Demo",
        model_name="builtin-demo",
        mode="demo",
        risk_level="low",
        knowledge_sources=[],
    )

    save_feedback(session_id, assistant_message_id, "helpful", "谢谢")

    with sqlite3.connect(database_path()) as connection:
        row = connection.execute(
            "SELECT rating, comment FROM feedback WHERE assistant_message_id = ?",
            (assistant_message_id,),
        ).fetchone()

    assert row == ("helpful", "谢谢")


def test_connect_returns_row_factory_connection(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "connect-test.db"))

    connection = connect()
    try:
        row = connection.execute("SELECT 1 AS value").fetchone()
    finally:
        connection.close()

    assert row["value"] == 1
