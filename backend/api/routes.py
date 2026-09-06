from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse

from services.auth import verify_api_key
from services.knowledge import (
    delete_knowledge_document,
    knowledge_document_count,
    list_knowledge_documents,
    search_knowledge,
    write_knowledge_document,
)
from services.storage import delete_session, list_recent_sessions, save_feedback, session_history
from services.telemetry import telemetry

from backend.chat_logic import to_knowledge_models
from backend.chat_service import handle_chat_request, handle_chat_stream
from backend.config import (
    SCENARIO_OPTIONS,
    STATIC_DIR,
    STYLE_OPTIONS,
    api_key_configured,
    configured_api_key_env,
    public_demo_mode,
    supports_temperature,
)
from backend.runtime import build_configured_target, evaluate_runtime_compatibility, list_model_options
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    CompatibilityReport,
    DeleteResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentSummary,
    KnowledgeDocumentUpsertResponse,
    KnowledgeSearchResponse,
    ScenarioOption,
    ServiceInfo,
    SessionHistoryResponse,
    SessionListResponse,
    SessionMessage,
    SessionSummary,
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


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> PlainTextResponse:
    """Prometheus-compatible scraping endpoint."""
    return PlainTextResponse(telemetry.format_prometheus(), media_type="text/plain; version=0.0.4")


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/api/meta", response_model=ServiceInfo)
def meta(request: Request) -> ServiceInfo:
    target = build_configured_target()
    return ServiceInfo(
        name=request.app.title,
        version=request.app.version,
        description="知愈星 AI (ZhiYuXing Copilot) · 企业级多场景心身关怀与行动赋能平台，支持高校与企业 EAP 双场景。",
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


@router.get("/api/scenarios", response_model=list[ScenarioOption])
def list_scenarios() -> list[ScenarioOption]:
    """List business scenarios (Campus vs Enterprise EAP)."""
    return SCENARIO_OPTIONS


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


@router.delete("/api/knowledge/documents/{document_id}", response_model=DeleteResponse)
def remove_knowledge_document(document_id: str) -> DeleteResponse:
    if public_demo_mode():
        raise HTTPException(status_code=403, detail="PUBLIC_DEMO_MODE=true，当前公开后端不允许删除知识文档。")
    deleted = delete_knowledge_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="自定义知识文档不存在或不可删除（内置文档受系统保护）。")
    return DeleteResponse(status="ok", message=f"知识文档 '{document_id}' 已成功从知识库删除。")


@router.get("/api/sessions", response_model=SessionListResponse)
def get_sessions(limit: int = Query(30, ge=1, le=100)) -> SessionListResponse:
    items = [SessionSummary(**item) for item in list_recent_sessions(limit=limit)]
    return SessionListResponse(total=len(items), sessions=items)


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


@router.delete("/api/sessions/{session_id}", response_model=DeleteResponse)
def remove_session(session_id: str) -> DeleteResponse:
    if public_demo_mode():
        raise HTTPException(status_code=403, detail="PUBLIC_DEMO_MODE=true，当前公开后端禁止删除会话。")
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或已清除。")
    return DeleteResponse(status="ok", message=f"会话 '{session_id}' 及其历史记录已清除。")


@router.post("/api/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    if public_demo_mode():
        raise HTTPException(status_code=403, detail="PUBLIC_DEMO_MODE=true，当前公开后端不记录反馈。")
    save_feedback(req.session_id, req.assistant_message_id, req.rating, req.comment)
    return FeedbackResponse(status="ok", message="反馈已记录，可用于后续改进回复质量。")


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _: Optional[str] = Depends(verify_api_key)) -> ChatResponse:
    return handle_chat_request(req)


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _: Optional[str] = Depends(verify_api_key)) -> StreamingResponse:
    """Enterprise SSE streaming endpoint for real-time typewriter output."""
    return StreamingResponse(
        handle_chat_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
