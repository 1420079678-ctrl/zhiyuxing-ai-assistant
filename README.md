# 知愈星 AI Assistant

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Demo-009688?logo=fastapi&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)

面向大学生场景的 AI 情绪支持与学习辅助原型项目，采用“可运行 Web Demo + FastAPI 后端 + 文档化方案说明”的方式组织，适合作为实习投递时展示 AI 应用落地、后端开发和工程化整理能力的 GitHub 项目。

`技术关键词：Python / FastAPI / OpenAI SDK / Prompt Engineering / Pydantic / Pytest / GitHub Actions / DingTalk Integration Design`

## 适合投递的岗位方向

- Python 后端开发实习
- AI 应用 / LLM 应用开发实习
- 偏产品理解的技术实习

## 1 分钟看点

- 可以直接本地启动独立 Web Demo，不依赖钉钉组织权限。
- 提供 `/chat`、`/health`、`/api/meta` 等接口，能快速体现后端结构。
- 通过系统提示词约束输出风格与安全边界，体现基础 Prompt 设计意识。
- 补充了 `pytest` 和 GitHub Actions CI，不只是“方案展示”，而是最小可运行交付。
- 单独说明钉钉接入的权限边界，避免把平台型方案误写成“任何人都可直接使用”。

## 项目定位

很多大学生面临的并不只是“不会学”，而是“在焦虑、拖延、自我怀疑的状态下很难重新开始”。这个项目尝试把“情绪支持”和“学习建议”放进同一个对话闭环中，用 AI 先帮助用户稳定状态，再给出可执行的小步行动建议。

当前 GitHub 版本强调的是可展示、可验证、可说明边界，而不是把作品集 Demo 包装成完整线上产品。

## 这个仓库能证明什么

| 能力维度 | 仓库证据 | 面试中可说明的点 |
| --- | --- | --- |
| AI 应用原型设计 | `/chat` 接口、系统提示词约束 | 不只是调用模型，还考虑场景、语气和边界 |
| 后端服务开发 | `app.py`、Pydantic 请求响应模型 | 具备基础 API 设计和服务封装能力 |
| 演示与交付意识 | `static/` 独立 Web Demo、根路由页面 | 外部评审可以直接体验，不被平台权限卡住 |
| 工程质量 | `tests/test_app.py`、`.github/workflows/ci.yml` | 具备最小测试和持续集成意识 |
| 平台集成边界表达 | `docs/dingtalk-integration.md` | 清楚区分“真实落地场景”和“作品集演示入口” |

## 已实现与规划中

| 状态 | 内容 |
| --- | --- |
| 已实现 | FastAPI 服务、Web Demo、`/chat` `/health` `/api/meta` 接口、基础 Prompt 约束、测试、CI、项目文档整理 |
| 规划中 | 知识库检索、风险词识别与转介流程、对话记录存储、真实钉钉授权接入 |

这种写法更适合实习投递，因为它既展示能力，也避免过度承诺。

## 页面预览

### 平台界面

![平台界面示意](docs/assets/09-platform-overview.png)

### 对话演示

![对话界面示意](docs/assets/10-chat-demo.png)

## 技术栈

- Python 3.13
- FastAPI
- OpenAI Python SDK
- Pydantic
- python-dotenv
- Pytest
- GitHub Actions

## 架构图

![技术架构图](docs/assets/07-technical-architecture.png)

## 快速启动

推荐使用 Python 3.13，以保持与当前本地开发和 CI 环境一致。

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

在 `.env` 中配置：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

### 3. 启动服务

```bash
python -m uvicorn app:app --reload
```

启动后可访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/meta`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### 4. 运行测试

```bash
python -m pytest -vv
```

## 接口示例

### `POST /chat`

```json
{
  "message": "这周压力很大，感觉完全学不进去。",
  "system_hint": "给出温和且可执行的建议"
}
```

```json
{
  "reply": "当前状态里明显存在压力堆积，可以先不追求一次解决整周问题，而是把任务缩小到今天最容易开始的一步，比如先完成 20 分钟复习。",
  "note": "这是作品集仓库中的最小可运行 Demo，用于展示项目方向与接口能力。"
}
```

## 文档入口

- [docs/project-report.md](docs/project-report.md)：完整项目报告与方案背景
- [docs/resume-interview-guide.md](docs/resume-interview-guide.md)：简历描述、自我介绍和投递表达
- [docs/interview-qa.md](docs/interview-qa.md)：面试高频追问速答
- [docs/dingtalk-integration.md](docs/dingtalk-integration.md)：钉钉权限模型与集成边界说明

## 钉钉相关说明

- 这个仓库默认以独立 Web Demo 作为演示入口，外部评审不需要使用个人账号权限。
- 如果项目以钉钉企业内部应用形态部署，访问能力会受到组织、管理员授权和应用类型限制。
- 因此钉钉更适合作为真实业务落地场景说明，而不是唯一 Demo 入口。
