from pathlib import Path

from services.knowledge import (
    detect_document_category,
    excerpt_text,
    list_knowledge_documents,
    relative_source_path,
    sanitize_document_id,
    search_knowledge,
    tokenize_text,
    write_knowledge_document,
)


def test_tokenize_text_supports_chinese_and_english() -> None:
    tokens = tokenize_text("考试 stress")

    assert "stress" in tokens
    assert "考试" in tokens


def test_sanitize_document_id_normalizes_title() -> None:
    assert sanitize_document_id(" Campus Support Guide 2026 ") == "campus-support-guide-2026"


def test_excerpt_text_truncates_long_content() -> None:
    excerpt = excerpt_text("a" * 200, limit=20)

    assert excerpt.endswith("…")
    assert len(excerpt) == 20


def test_write_knowledge_document_and_search(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("KNOWLEDGE_UPLOAD_DIR", str(tmp_path / "uploads"))
    unique_keyword = "knowledge_write_marker_2026"

    document = write_knowledge_document(
        "自定义支持文档",
        f"这是一段用于测试知识写入和检索的内容，包含唯一标记 {unique_keyword}。",
    )
    hits = search_knowledge(unique_keyword, limit=5)

    assert document.category == "custom"
    assert any("knowledge_write_marker_2026" in hit.excerpt or "uploads" in hit.source_path for hit in hits)


def test_list_knowledge_documents_contains_builtin_documents() -> None:
    documents = list_knowledge_documents()

    assert documents
    assert any(item.category == "builtin" for item in documents)


def test_relative_source_path_supports_external_temp_paths(tmp_path) -> None:
    path = tmp_path / "external.md"
    path.write_text("# temp\n\ncontent", encoding="utf-8")

    source_path = relative_source_path(path)

    assert str(path.resolve()).replace("\\", "/") == source_path


def test_detect_document_category_for_external_file_is_unknown(tmp_path) -> None:
    path = tmp_path / "external.md"
    path.write_text("# temp\n\ncontent", encoding="utf-8")

    assert detect_document_category(path) == "unknown"
