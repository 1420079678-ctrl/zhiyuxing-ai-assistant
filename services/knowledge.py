from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
DEFAULT_UPLOAD_DIR = BASE_DIR / "data" / "knowledge_uploads"


@dataclass(frozen=True)
class KnowledgeHitResult:
    title: str
    excerpt: str
    source_path: str
    score: float


@dataclass(frozen=True)
class KnowledgeChunk:
    title: str
    source_path: str
    content: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeDocumentResult:
    document_id: str
    title: str
    source_path: str
    category: str


def builtin_knowledge_dir() -> Path:
    configured = os.getenv("KNOWLEDGE_BASE_DIR", "").strip()
    return Path(configured) if configured else DEFAULT_KNOWLEDGE_DIR


def upload_knowledge_dir() -> Path:
    configured = os.getenv("KNOWLEDGE_UPLOAD_DIR", "").strip()
    return Path(configured) if configured else DEFAULT_UPLOAD_DIR


def knowledge_directories() -> list[tuple[str, Path]]:
    return [
        ("builtin", builtin_knowledge_dir()),
        ("custom", upload_knowledge_dir()),
    ]


def tokenize_text(text: str) -> list[str]:
    lowered = text.lower()
    english_tokens = re.findall(r"[a-z0-9_]+", lowered)
    chinese_sequences = re.findall(r"[\u4e00-\u9fff]{2,}", text)

    cjk_tokens: list[str] = []
    for sequence in chinese_sequences:
        if len(sequence) <= 4:
            cjk_tokens.append(sequence)
        for index in range(len(sequence) - 1):
            cjk_tokens.append(sequence[index : index + 2])

    single_terms = re.findall(r"[\u4e00-\u9fff]", text)
    return english_tokens + cjk_tokens + single_terms


def knowledge_document_count() -> int:
    return len(iter_knowledge_files())


def iter_knowledge_files() -> list[Path]:
    files: list[Path] = []
    for _, directory in knowledge_directories():
        if not directory.exists():
            continue
        files.extend(
            [
                path
                for path in directory.iterdir()
                if path.suffix.lower() in {".md", ".txt"} and path.is_file()
            ]
        )
    return sorted(files)


def load_knowledge_chunks() -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for path in iter_knowledge_files():
        chunks.extend(parse_knowledge_file(path))
    return chunks


def detect_document_category(path: Path) -> str:
    builtin_dir = builtin_knowledge_dir().resolve()
    upload_dir = upload_knowledge_dir().resolve()
    resolved = path.resolve()

    if resolved.is_relative_to(builtin_dir):
        return "builtin"
    if resolved.is_relative_to(upload_dir):
        return "custom"
    return "unknown"


def relative_source_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(BASE_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def extract_document_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem.replace("-", " ")
    return path.stem.replace("-", " ")


def list_knowledge_documents() -> list[KnowledgeDocumentResult]:
    return [
        KnowledgeDocumentResult(
            document_id=path.stem,
            title=extract_document_title(path),
            source_path=relative_source_path(path),
            category=detect_document_category(path),
        )
        for path in iter_knowledge_files()
    ]


def sanitize_document_id(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"\s+", "-", lowered)
    lowered = re.sub(r"[^a-z0-9\-_]+", "-", lowered)
    normalized = re.sub(r"-{2,}", "-", lowered).strip("-_")
    return normalized or "custom-knowledge"


def write_knowledge_document(title: str, content: str, document_id: str | None = None) -> KnowledgeDocumentResult:
    upload_dir = upload_knowledge_dir()
    upload_dir.mkdir(parents=True, exist_ok=True)

    resolved_id = sanitize_document_id(document_id or title)
    target_path = upload_dir / f"{resolved_id}.md"
    payload = f"# {title.strip()}\n\n{content.strip()}\n"
    target_path.write_text(payload, encoding="utf-8")

    return KnowledgeDocumentResult(
        document_id=resolved_id,
        title=title.strip(),
        source_path=relative_source_path(target_path),
        category="custom",
    )


def delete_knowledge_document(document_id: str) -> bool:
    resolved_id = sanitize_document_id(document_id)
    target_path = upload_knowledge_dir() / f"{resolved_id}.md"
    if target_path.exists() and target_path.is_file():
        target_path.unlink()
        return True
    return False


def parse_knowledge_file(path: Path) -> list[KnowledgeChunk]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    chunks: list[KnowledgeChunk] = []
    current_title = path.stem.replace("-", " ")
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        content = " ".join(line.strip() for line in buffer if line.strip()).strip()
        buffer.clear()
        if len(content) < 20:
            return
        chunks.append(
            KnowledgeChunk(
                title=current_title,
                source_path=relative_source_path(path),
                content=content,
                tokens=tuple(tokenize_text(content)),
            )
        )

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            current_title = stripped.lstrip("#").strip() or current_title
            continue
        if not stripped:
            flush()
            continue
        buffer.append(stripped)

    flush()
    return chunks


def excerpt_text(text: str, limit: int = 120) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def score_chunk(query: str, query_tokens: list[str], chunk: KnowledgeChunk) -> float:
    if not query_tokens:
        return 0.0

    token_set = set(chunk.tokens)
    overlap = sum(1.0 for token in query_tokens if token in token_set)
    title_bonus = sum(0.6 for token in query_tokens if token and token in chunk.title.lower())
    phrase_bonus = 0.0
    lowered_query = query.lower()
    lowered_content = chunk.content.lower()
    if len(lowered_query) >= 4 and lowered_query in lowered_content:
        phrase_bonus += 2.0
    if len(lowered_query) >= 2 and lowered_query in chunk.title.lower():
        phrase_bonus += 1.6
    return overlap + title_bonus + phrase_bonus


def search_knowledge(query: str, limit: int = 3) -> list[KnowledgeHitResult]:
    normalized = query.strip()
    if len(normalized) < 2:
        return []

    query_tokens = tokenize_text(normalized)
    ranked: list[tuple[float, KnowledgeChunk]] = []
    for chunk in load_knowledge_chunks():
        score = score_chunk(normalized, query_tokens, chunk)
        if score <= 0:
            continue
        ranked.append((score, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        KnowledgeHitResult(
            title=chunk.title,
            excerpt=excerpt_text(chunk.content),
            source_path=chunk.source_path,
            score=round(score, 2),
        )
        for score, chunk in ranked[:limit]
    ]
