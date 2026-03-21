from __future__ import annotations

import secrets
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
    provider_name: str
    model_name: str
    base_url: str
    model_doc: str
    supports_temperature: bool


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def resolve_api_key() -> Optional[str]:
    for env_name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY"):
        value = os.getenv(env_name)
        if value:
            return value
    return None


def api_key_configured() -> bool:
    return bool(resolve_api_key())


def current_model_name() -> str:
    return os.getenv("MODEL_NAME", "gpt-4o-mini")


def current_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


def configured_provider_name() -> str:
    configured = os.getenv("MODEL_PROVIDER")
    if configured:
        return configured

    base_url = current_base_url().lower()
    model_name = current_model_name().lower()

    if "deepseek" in base_url or model_name.startswith("deepseek"):
        return "DeepSeek"
    if "openai" in base_url or model_name.startswith("gpt"):
        return "OpenAI"
    return "OpenAI Compatible"


def active_model_name() -> str:
    if current_chat_mode() == "demo":
        return "builtin-demo"
    return current_model_name()


def active_base_url() -> str:
    if current_chat_mode() == "demo":
        return "local://demo-fallback"
    return current_base_url()


def current_provider_name() -> str:
    if current_chat_mode() == "demo":
        return "Local Demo"
    return configured_provider_name()


def current_temperature() -> float:
    raw_value = os.getenv("MODEL_TEMPERATURE", "0.7")
    try:
        return float(raw_value)
    except ValueError:
        return 0.7


def supports_temperature(model_name: Optional[str] = None) -> bool:
    return (model_name or current_model_name()).lower() != "deepseek-reasoner"


def current_chat_mode() -> str:
    if env_flag("DEMO_MODE"):
        return "demo"
    return "openai" if api_key_configured() else "demo"


def build_client() -> OpenAI:
    api_key = resolve_api_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="缺少模型密钥，请先在 .env 中配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY",
        )

    base_url = current_base_url()
    return OpenAI(api_key=api_key, base_url=base_url)


def build_completion_kwargs(messages: list[dict[str, str]]) -> dict[str, object]:
    model_name = current_model_name()
    payload: dict[str, object] = {
        "model": model_name,
        "messages": messages,
    }

    if supports_temperature(model_name):
        payload["temperature"] = current_temperature()

    return payload


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


def detect_demo_style(system_hint: Optional[str]) -> str:
    hint = (system_hint or "").strip()

    if any(keyword in hint for keyword in ("简洁", "简短", "直接")):
        return "brief"
    if any(keyword in hint for keyword in ("鼓励", "打气", "积极")):
        return "encouraging"
    if any(keyword in hint for keyword in ("结构", "分点", "计划", "步骤清晰")):
        return "structured"
    if any(keyword in hint for keyword in ("温柔", "陪伴", "安抚", "共情")):
        return "warm"
    return "balanced"


def render_demo_reply(opening: str, steps: list[str], closing: str, style: str) -> str:
    action_list = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))

    if style == "brief":
        return f"{opening}\n\n先做这 3 件事：\n{action_list}\n\n{closing}"
    if style == "encouraging":
        return (
            f"{opening}\n\n你不用一次把状态拉满，先拿回一点点主动权就够了：\n"
            f"{action_list}\n\n{closing}"
        )
    if style == "structured":
        return (
            f"{opening}\n\n当前更适合的顺序是：先稳住情绪，再缩小任务，最后决定是否继续推进。\n\n"
            f"建议按下面 3 步来：\n{action_list}\n\n{closing}"
        )
    if style == "warm":
        return (
            f"{opening}\n\n你现在不需要马上变得高效，先让自己从最难受的状态里稍微退出来一点就好。\n\n"
            f"可以温和地试这 3 步：\n{action_list}\n\n{closing}"
        )

    return f"{opening}\n\n可以先试试这 3 步：\n{action_list}\n\n{closing}"


def build_demo_reply(user_message: str, system_hint: Optional[str] = None) -> str:
    text = user_message.strip()
    style = detect_demo_style(system_hint)

    if any(keyword in text for keyword in ("焦虑", "压力", "慌", "紧张", "崩溃", "面试", "考试")):
        openings = [
            "能感觉到你现在已经被压力推得很紧了，先别要求自己立刻恢复到高效率。",
            "你现在更像是被压力一直顶着走，越想快点进入状态，越容易更慌。",
            "这种紧绷感很常见，尤其在考试、面试或任务堆积的时候，大脑会先被压力占满。",
        ]
        step_sets = [
            [
                "把目标缩到 15 分钟，只做一件最容易开始的小任务，比如整理提纲或看两页笔记。",
                "写下眼下最担心的一件事，再写一个能在今天完成的应对动作，避免脑子里反复打转。",
                "做完这一小步后先暂停 3 分钟，喝水、走动或深呼吸，再决定要不要继续下一步。",
            ],
            [
                "先把“我要赶紧恢复状态”改成“我先完成一个最小动作”，降低启动门槛。",
                "把今天的任务压缩成 1 个核心目标和 1 个保底目标，别让任务列表继续扩大压力。",
                "如果心跳快、脑子乱，先离开屏幕两三分钟，再回来处理最小那一项。",
            ],
            [
                "先不要整块规划整天，只选现在最容易动手的一件事。",
                "把担心写成一句话，再在后面补一句“我此刻能做的是……”，把注意力拉回行动。",
                "完成后给自己一个暂停点，不要一开始就要求连续高强度推进。",
            ],
        ]
        closings = [
            "如果这种压迫感已经持续很久，或者已经影响到睡眠、饮食和日常功能，建议尽快联系学校心理中心、辅导员或可信任的成年人获得线下支持。",
            "如果这种紧绷状态已经连续很多天，甚至开始影响睡眠和日常生活，最好尽快找学校心理中心、辅导员或可信任的人聊一聊。",
            "如果压力已经超出自己能慢慢消化的范围，及时寻求线下支持会比一个人硬扛更有效。",
        ]
    elif any(keyword in text for keyword in ("拖延", "不想学", "学不进去", "烦躁", "内耗")):
        openings = [
            "这更像是启动成本被情绪放大了，不一定是能力不够。",
            "很多时候拖延不是因为不重视，而是大脑把“开始”这一步放大得太难了。",
            "你现在卡住的点，未必是不会做，而是情绪和任务量一起把启动门槛抬高了。",
        ]
        step_sets = [
            [
                "先不要追求完整学习流程，只做一个 10 到 15 分钟的启动动作。",
                "把任务拆成可以立刻执行的最小步骤，例如打开资料、写标题、列 3 个要点。",
                "完成后给自己一个明确反馈，比如勾掉清单中的第一项，帮助大脑建立“我已经开始了”的信号。",
            ],
            [
                "先选一件最不费力的动作开始，比如打开课件、整理目录或写下要复习的 3 个主题。",
                "把“学一晚上”改成“先做 15 分钟”，先让身体和注意力进入任务。",
                "只要开始了，就允许自己在第一个时间块结束后决定是否继续，不要提前把整晚都想完。",
            ],
            [
                "把当前任务写成一句最小指令，例如“先看第一页并画出重点”。",
                "先把手机、聊天窗口或最容易分心的页面关掉 15 分钟，帮自己减少内耗来源。",
                "做完之后马上记录“我已经推进到哪一步”，不要让大脑继续把事情想成完全没动。",
            ],
        ]
        closings = [
            "如果拖延和烦躁已经持续很久，也可以留意最近是不是压力、睡眠或情绪状态本身就在消耗你。",
            "如果这种内耗已经变成长期状态，最好连同作息、压力源和情绪一起看，而不是只盯着“自律”两个字。",
            "如果你发现自己长期都在这种启动困难里打转，也值得尽快和身边可信任的人聊聊最近的压力来源。",
        ]
    elif any(keyword in text for keyword in ("失眠", "睡不着", "很累", "熬夜", "没精神")):
        openings = [
            "现在更重要的是先把状态稳住，而不是继续硬扛。",
            "如果身体已经很累，继续逼自己往前推，通常只会让烦躁和低效更明显。",
            "当睡眠和精力状态已经受影响时，先恢复一点基本状态，比继续加码任务更关键。",
        ]
        step_sets = [
            [
                "优先保证一段不被打断的休息时间，哪怕先从短暂闭眼和离开屏幕开始。",
                "把今天必须完成的事压缩到最关键的一项，减少因为任务过多带来的额外消耗。",
                "如果连续多天睡眠和精神状态都很差，尽快找校医院、心理中心或可信任的人聊一聊。",
            ],
            [
                "先暂停继续堆任务，给自己留一段真正不处理信息的缓冲时间。",
                "把今天的目标改成“保住最重要的一件事”，不要再对自己追加额外要求。",
                "如果已经连续几天睡不好，别只靠硬撑，尽快考虑线下求助或就医。",
            ],
            [
                "先把屏幕和高刺激信息关掉几分钟，让身体有机会慢下来。",
                "给今天的任务减负，只留最核心的一项，其他往后顺延。",
                "一旦发现失眠和疲惫已经持续，就要把它当成需要认真处理的信号，而不是小问题。",
            ],
        ]
        closings = [
            "如果这种状态已经连续几天甚至更久，尽快联系校医院、心理中心或可信任的成年人会更稳妥。",
            "如果疲惫和睡眠问题已经明显影响学习和生活，建议尽快找线下支持，不必一个人扛。",
            "如果已经出现持续失眠或明显的身心耗竭，及时寻求专业帮助会比继续硬撑更有效。",
        ]
    else:
        openings = [
            "你现在的状态值得先被看见，不需要一开始就把所有问题一次解决。",
            "先别急着要求自己立刻想明白全部，很多问题都是在行动里慢慢变清楚的。",
            "现在更适合先把问题收窄，而不是一上来就要求自己把整件事想透。",
        ]
        step_sets = [
            [
                "先说清楚眼下最困扰你的一个点，把问题收窄到可处理的范围内。",
                "给自己设一个很小的行动目标，优先恢复一点点掌控感。",
                "完成后再决定下一步，而不是一开始就要求自己把整件事做完。",
            ],
            [
                "先把“我到底怎么了”换成“我现在最卡的是哪一步”，减少模糊焦虑。",
                "只挑一个今天能推进的小动作，先把注意力从担心拉回到行动。",
                "做完这一小步后，再看需不需要继续，而不是提前被整件事压住。",
            ],
            [
                "用一句话写下你现在最想解决的核心问题。",
                "把它拆成一个今天能完成的小步骤，哪怕只推进 10 分钟也可以。",
                "先完成这一步，再重新判断接下来最值得做什么。",
            ],
        ]
        closings = [
            "如果你愿意，也可以继续把当前最卡的那个点说得更具体一点，我再帮你一起拆。",
            "如果这种状态已经持续很久，或者已经明显影响到日常生活，也值得尽快找线下支持一起处理。",
            "如果你发现自己已经长期被这类问题困住，及时和可信任的人或专业老师聊聊会更有帮助。",
        ]

    opening = secrets.choice(openings)
    steps = secrets.choice(step_sets)
    closing = secrets.choice(closings)
    return render_demo_reply(opening, steps, closing, style)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "zhiyuxing-ai-assistant",
        "version": app.version,
        "mode": current_chat_mode(),
        "api_key_configured": api_key_configured(),
        "provider_name": current_provider_name(),
        "model_name": active_model_name(),
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
        provider_name=current_provider_name(),
        model_name=active_model_name(),
        base_url=active_base_url(),
        model_doc="/project-docs/model-integration.md",
        supports_temperature=supports_temperature(),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    mode = current_chat_mode()

    if mode == "demo":
        return ChatResponse(
            reply=build_demo_reply(req.message, req.system_hint),
            note="当前为本地演示模式。系统会根据输入内容和补充要求切换不同的演示话术；如需真实模型效果，仍需要接入实际模型后端。",
            mode=mode,
        )

    try:
        client = build_client()
        completion = client.chat.completions.create(
            **build_completion_kwargs(build_messages(req.message, req.system_hint))
        )
        reply = completion.choices[0].message.content or "抱歉，我这次没有成功生成回复。"
        return ChatResponse(
            reply=reply,
            note=f"当前为模型调用模式。回复由 {current_provider_name()} / {current_model_name()} 生成。",
            mode=mode,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"调用模型失败：{exc}") from exc
