from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入")
    system_hint: Optional[str] = Field(default=None, description="可选的额外系统提示")
    response_style: Optional[str] = Field(default="balanced", description="回答风格")
    model_target: Optional[str] = Field(default="configured", description="模型目标")
    session_id: Optional[str] = Field(default=None, description="会话 ID；为空时自动创建")


class RetrievedKnowledge(BaseModel):
    title: str
    excerpt: str
    source_path: str
    score: float


class SafetyInfo(BaseModel):
    level: str
    label: str
    note: str
    needs_human_support: bool
    matched_keywords: list[str]


class ChatResponse(BaseModel):
    reply: str
    note: str
    mode: str
    provider_name: str
    model_name: str
    response_style: str
    session_id: str
    assistant_message_id: int
    memory_messages_used: int
    knowledge_hits: list[RetrievedKnowledge]
    safety: SafetyInfo


class ModelOption(BaseModel):
    id: str
    label: str
    provider_name: str
    model_name: str
    mode: str
    available: bool
    reason: Optional[str] = None


class StyleOption(BaseModel):
    id: str
    label: str
    helper_text: str


class ServiceInfo(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
    healthcheck: str
    demo_page: str
    deployment_note: str
    compatibility_url: str
    chat_mode: str
    api_key_configured: bool
    api_key_env: Optional[str]
    provider_name: str
    model_name: str
    base_url: str
    model_doc: str
    supports_temperature: bool
    persistence_enabled: bool
    knowledge_document_count: int
    session_history_url: str
    feedback_url: str
    knowledge_search_url: str
    knowledge_documents_url: str
    knowledge_upload_url: str
    available_models: list[ModelOption]
    available_styles: list[StyleOption]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    mode: str
    api_key_configured: bool
    api_key_env: Optional[str]
    provider_name: str
    model_name: str
    persistence_enabled: bool
    knowledge_document_count: int


class CompatibilityCheckItem(BaseModel):
    code: str
    status: str
    message: str


class QuickSetupOption(BaseModel):
    id: str
    label: str
    command: str
    description: str


class CompatibilityReport(BaseModel):
    status: str
    summary: str
    ready_for_model_call: bool
    mode: str
    provider_name: str
    model_name: str
    base_url: str
    api_key_env: Optional[str]
    api_key_configured: bool
    supports_temperature: bool
    checks: list[CompatibilityCheckItem]
    recommended_setups: list[QuickSetupOption]


class SessionMessage(BaseModel):
    id: int
    role: str
    content: str
    provider_name: Optional[str] = None
    model_name: Optional[str] = None
    mode: Optional[str] = None
    risk_level: Optional[str] = None
    created_at: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    title: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    total_messages: int
    messages: list[SessionMessage]


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_hits: int
    hits: list[RetrievedKnowledge]


class KnowledgeDocumentSummary(BaseModel):
    document_id: str
    title: str
    source_path: str
    category: str


class KnowledgeDocumentListResponse(BaseModel):
    total_documents: int
    documents: list[KnowledgeDocumentSummary]


class KnowledgeDocumentCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=20, description="Markdown 或纯文本内容")
    document_id: Optional[str] = Field(default=None, description="可选文档 ID；为空时按标题生成")


class KnowledgeDocumentUpsertResponse(BaseModel):
    status: str
    message: str
    document: KnowledgeDocumentSummary


class FeedbackRequest(BaseModel):
    session_id: str
    assistant_message_id: int
    rating: Literal["helpful", "needs_more"]
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str


@dataclass(frozen=True)
class ResolvedTarget:
    id: str
    label: str
    mode: str
    provider_name: str
    model_name: str
    base_url: str
    api_key: Optional[str] = None
    api_key_env: Optional[str] = None


@dataclass(frozen=True)
class ModelPreset:
    id: str
    label: str
    provider_name: str
    model_name: str
    base_url: str
    api_key_env: str
    mode: str = "openai"
