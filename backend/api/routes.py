from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse

from services.knowledge import knowledge_document_count, list_knowledge_documents, search_knowledge, write_knowledge_document
from services.storage import save_feedback, session_history

from backend.chat_logic import to_knowledge_models
from backend.chat_service import handle_chat_request
from backend.config import STATIC_DIR, STYLE_OPTIONS, api_key_configured, configured_api_key_env, public_demo_mode, supports_temperature
from backend.runtime import build_configured_target, evaluate_runtime_compatibility, list_model_options
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    CompatibilityReport,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentSummary,
    KnowledgeDocumentUpsertResponse,
    KnowledgeSearchResponse,
    ServiceInfo,
    SessionHistoryResponse,
    SessionMessage,
)


router = APIRouter()


def to_document_model(document) -> KnowledgeDocumentSummary:
    return KnowledgeDocumentSummary(
        document_id=document.document_id,
        title=document.title,
        source_path=document.source_path,
        category=document.category,
    )


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    target = build_configured_target()
    return HealthResponse(
        status="ok",
        service="zhiyuxing-ai-assistant",
        version=request.app.version,
        mode=target.mode,
        api_key_configured=api_key_configured(),
        api_key_env=configured_api_key_env(),
        provider_name=target.provider_name,
        model_name=target.model_name,
        persistence_enabled=True,
        knowledge_document_count=knowledge_document_count(),
    )


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/api/meta", response_model=ServiceInfo)
def meta(request: Request) -> ServiceInfo:
    target = build_configured_target()
    return ServiceInfo(
        name=request.app.title,
        version=request.app.version,
        description="可直接运行的 AI 情绪支持与学习辅助服务，支持本地演示模式和模型调用模式。",
        docs_url="/docs",
        healthcheck="/health",
        demo_page="/",
        deployment_note="/project-docs/dingtalk-integration.md",
        compatibility_url="/api/compatibility",
        chat_mode=target.mode,
        public_demo_mode=public_demo_mode(),
        api_key_configured=api_key_configured(),
        api_key_env=configured_api_key_env(),
        provider_name=target.provider_name,
        model_name=target.model_name,
        base_url=target.base_url,
        model_doc="/project-docs/model-integration.md",
        supports_temperature=supports_temperature(target.model_name),
        persistence_enabled=True,
        knowledge_document_count=knowledge_document_count(),
        session_history_url="/api/session/{session_id}",
        feedback_url="/api/feedback",
        knowledge_search_url="/api/knowledge/search?q=关键词",
        knowledge_documents_url="/api/knowledge/documents",
        knowledge_upload_url="/api/knowledge/documents",
        available_models=list_model_options(),
        available_styles=STYLE_OPTIONS,
    )


@router.get("/api/compatibility", response_model=CompatibilityReport)
def compatibility() -> CompatibilityReport:
    return evaluate_runtime_compatibility()


@router.get("/api/knowledge/search", response_model=KnowledgeSearchResponse)
def knowledge_search(q: str = Query(..., min_length=2, description="检索关键词")) -> KnowledgeSearchResponse:
    hits = search_knowledge(q)
    return KnowledgeSearchResponse(query=q, total_hits=len(hits), hits=to_knowledge_models(hits))


@router.get("/api/knowledge/documents", response_model=KnowledgeDocumentListResponse)
def knowledge_documents() -> KnowledgeDocumentListResponse:
    documents = [to_document_model(item) for item in list_knowledge_documents()]
    return KnowledgeDocumentListResponse(total_documents=len(documents), documents=documents)


@router.post("/api/knowledge/documents", response_model=KnowledgeDocumentUpsertResponse, status_code=201)
def create_knowledge_document(req: KnowledgeDocumentCreateRequest) -> KnowledgeDocumentUpsertResponse:
    if public_demo_mode():
        raise HTTPException(status_code=403, detail="PUBLIC_DEMO_MODE=true，当前公开后端不允许写入知识文档。")
    document = write_knowledge_document(req.title, req.content, req.document_id)
    return KnowledgeDocumentUpsertResponse(
        status="ok",
        message="知识文档已写入自定义知识库，可立即参与后续检索和回答。",
        document=to_document_model(document),
    )


@router.get("/api/session/{session_id}", response_model=SessionHistoryResponse)
def get_session_history(session_id: str) -> SessionHistoryResponse:
    payload = session_history(session_id)
    return SessionHistoryResponse(
        session_id=payload["session_id"],
        title=payload["title"],
        created_at=payload["created_at"],
        updated_at=payload["updated_at"],
        total_messages=payload["total_messages"],
        messages=[SessionMessage(**message) for message in payload["messages"]],
    )


@router.post("/api/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    if public_demo_mode():
        raise HTTPException(status_code=403, detail="PUBLIC_DEMO_MODE=true，当前公开后端不记录反馈。")
    save_feedback(req.session_id, req.assistant_message_id, req.rating, req.comment)
    return FeedbackResponse(status="ok", message="反馈已记录，可用于后续改进回复质量。")


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return handle_chat_request(req)
