from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"


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


def knowledge_dir() -> Path:
    return DEFAULT_KNOWLEDGE_DIR


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
    return len(list(iter_knowledge_files()))


def iter_knowledge_files() -> list[Path]:
    directory = knowledge_dir()
    if not directory.exists():
        return []
    return sorted(
        [path for path in directory.iterdir() if path.suffix.lower() in {".md", ".txt"} and path.is_file()]
    )


def load_knowledge_chunks() -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for path in iter_knowledge_files():
        chunks.extend(parse_knowledge_file(path))
    return chunks


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
                source_path=str(path.relative_to(BASE_DIR)).replace("\\", "/"),
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
