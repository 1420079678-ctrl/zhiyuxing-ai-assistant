import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def test_client(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("CHAT_DB_PATH", str(tmp_path / "zhiyuxing-test.db"))
    monkeypatch.setenv("KNOWLEDGE_UPLOAD_DIR", str(tmp_path / "knowledge_uploads"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.delenv("PUBLIC_DEMO_MODE", raising=False)

    with TestClient(app) as client:
        yield client
