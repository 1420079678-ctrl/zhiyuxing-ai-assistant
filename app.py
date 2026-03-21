from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

app = FastAPI(
    title="Zhiyuxing AI Assistant API",
    description="面向大学生场景的 AI 情绪支持与学习辅助服务，支持本地演示模式与模型调用模式。",
    version="0.3.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/project-docs", StaticFiles(directory=DOCS_DIR), name="project-docs")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入")
    system_hint: Optional[str] = Field(default=None, description="可选的额外系统提示")


class ChatResponse(BaseModel):
    reply: str
    note: str
    mode: str


class ServiceInfo(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
    healthcheck: str
    demo_page: str
    deployment_note: str
    chat_mode: str
    api_key_configured: bool


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def api_key_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def current_chat_mode() -> str:
    if env_flag("DEMO_MODE"):
        return "demo"
    return "openai" if api_key_configured() else "demo"


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="缺少 OPENAI_API_KEY，请先配置 .env")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def build_messages(user_message: str, system_hint: Optional[str]) -> list[dict[str, str]]:
    system_prompt = (
        "你是一个面向大学生的 AI 心理支持与学习辅助助手。"
        "回答时保持温和、具体、不过度承诺，不将自己描述为专业心理医生。"
        "优先做三件事：识别情绪、给出可执行的小建议、必要时提醒寻求线下专业帮助。"
        "不要输出诊断结论，不要给出危险、自伤或伤人建议。"
    )
    if system_hint:
        system_prompt += "\n补充要求：" + system_hint

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def build_demo_reply(user_message: str) -> str:
    text = user_message.strip()

    if any(keyword in text for keyword in ("焦虑", "压力", "慌", "紧张", "崩溃", "面试", "考试")):
        summary = "能感觉到你现在已经被压力推得很紧了，先别要求自己立刻恢复到高效率。"
        steps = [
            "把目标缩到 15 分钟，只做一件最容易开始的小任务，比如整理提纲或看两页笔记。",
            "写下眼下最担心的一件事，再写一个能在今天完成的应对动作，避免脑子里反复打转。",
            "做完这一小步后先暂停 3 分钟，喝水、走动或深呼吸，再决定要不要继续下一步。",
        ]
    elif any(keyword in text for keyword in ("拖延", "不想学", "学不进去", "烦躁", "内耗")):
        summary = "这更像是启动成本被情绪放大了，不一定是能力不够。"
        steps = [
            "先不要追求完整学习流程，只做一个 10 到 15 分钟的启动动作。",
            "把任务拆成可以立刻执行的最小步骤，例如打开资料、写标题、列 3 个要点。",
            "完成后给自己一个明确反馈，比如勾掉清单中的第一项，帮助大脑建立“我已经开始了”的信号。",
        ]
    elif any(keyword in text for keyword in ("失眠", "睡不着", "很累", "熬夜", "没精神")):
        summary = "现在更重要的是先把状态稳住，而不是继续硬扛。"
        steps = [
            "优先保证一段不被打断的休息时间，哪怕先从短暂闭眼和离开屏幕开始。",
            "把今天必须完成的事压缩到最关键的一项，减少因为任务过多带来的额外消耗。",
            "如果连续多天睡眠和精神状态都很差，尽快找校医院、心理中心或可信任的人聊一聊。",
        ]
    else:
        summary = "你现在的状态值得先被看见，不需要一开始就把所有问题一次解决。"
        steps = [
            "先说清楚眼下最困扰你的一个点，把问题收窄到可处理的范围内。",
            "给自己设一个很小的行动目标，优先恢复一点点掌控感。",
            "完成后再决定下一步，而不是一开始就要求自己把整件事做完。",
        ]

    closing = (
        "如果这种压迫感已经持续很久，或者已经影响到睡眠、饮食和日常功能，"
        "建议尽快联系学校心理中心、辅导员或可信任的成年人获得线下支持。"
    )

    action_list = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    return f"{summary}\n\n可以先试试这 3 步：\n{action_list}\n\n{closing}"


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "zhiyuxing-ai-assistant",
        "version": app.version,
        "mode": current_chat_mode(),
        "api_key_configured": api_key_configured(),
    }


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/meta", response_model=ServiceInfo)
def meta() -> ServiceInfo:
    return ServiceInfo(
        name=app.title,
        version=app.version,
        description="可直接运行的 AI 情绪支持与学习辅助服务，支持本地演示模式和模型调用模式。",
        docs_url="/docs",
        healthcheck="/health",
        demo_page="/",
        deployment_note="/project-docs/dingtalk-integration.md",
        chat_mode=current_chat_mode(),
        api_key_configured=api_key_configured(),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    mode = current_chat_mode()

    if mode == "demo":
        return ChatResponse(
            reply=build_demo_reply(req.message),
            note="当前为本地演示模式。未配置模型密钥时，系统会返回内置的支持性建议，便于直接运行、体验和继续开发。",
            mode=mode,
        )

    try:
        client = build_client()
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        completion = client.chat.completions.create(
            model=model_name,
            messages=build_messages(req.message, req.system_hint),
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or "抱歉，我这次没有成功生成回复。"
        return ChatResponse(
            reply=reply,
            note="当前为模型调用模式。回复由配置的 OpenAI 兼容接口生成。",
            mode=mode,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"调用模型失败：{exc}") from exc
