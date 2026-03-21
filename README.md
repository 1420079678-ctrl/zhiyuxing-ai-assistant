# 知愈星 AI Assistant

知愈星是一个面向大学生场景的 AI 心理支持与学习辅助助手，围绕“情绪支持 + 学习指导”两条主线，尝试把共情式对话、行动建议和校园使用场景结合起来。

这个仓库适合用作实习作品集展示，因为它同时保留了两个层面：

- 一个可以本地运行的最小后端 Demo；
- 一份完整整理过的项目方案文档、流程图和界面示意；
- 清晰体现了产品思考、接口设计、提示工程和安全边界意识。

## 项目亮点

- 场景聚焦：针对大学生常见的学业压力、社交焦虑、拖延和学习内耗设计对话方向。
- 双线联动：不是只做“心理安慰”，而是把情绪支持和学习建议做成一个连续闭环。
- 可运行展示：仓库提供 FastAPI Demo，可直接接入 OpenAI 兼容模型进行对话测试。
- 伦理边界明确：回复中避免诊断化表达，对高风险场景保留转介意识，不把 AI 包装成专业医疗替代。

## 当前仓库包含什么

- `app.py`：最小可运行 API，提供 `/`、`/health` 和 `/chat` 接口。
- `docs/project-report.md`：完整项目报告，包含定位、功能设计、创新点和技术方案。
- `docs/assets/`：流程图、架构图和界面示意图。
- `requirements.txt`：运行 Demo 所需依赖。

## 技术栈

- Python
- FastAPI
- OpenAI Python SDK
- Pydantic
- python-dotenv

## 页面预览

### 平台界面

![平台界面示意](docs/assets/09-platform-overview.png)

### 对话演示

![对话界面示意](docs/assets/10-chat-demo.png)

## 项目结构

```text
zhiyuxing-ai-assistant/
├── app.py
├── requirements.txt
├── .env.example
└── docs/
    ├── project-report.md
    └── assets/
        ├── 02-project-goals-flow.png
        ├── 03-core-features-flow.png
        ├── 04-innovation-workflow.png
        ├── 05-heart-learning-loop.png
        ├── 06-practicality-flow.png
        ├── 07-technical-architecture.png
        ├── 08-service-closed-loop.png
        ├── 09-platform-overview.png
        └── 10-chat-demo.png
```

## 快速启动

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

在 `.env` 中配置以下内容：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

### 3. 启动服务

```bash
uvicorn app:app --reload
```

启动后可以访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## 接口示例

### `POST /chat`

请求体：

```json
{
  "message": "这周压力很大，感觉完全学不进去。",
  "system_hint": "给出温和且可执行的建议"
}
```

返回示例：

```json
{
  "reply": "我能感觉到你现在有点被压力压住了。我们先不要急着把一整周的问题一次解决，可以先挑今天最小的一件事开始，比如只完成 20 分钟复习...",
  "note": "这是作品集仓库中的最小可运行 Demo，用于展示项目方向与接口能力。"
}
```

## 文档入口

- 完整项目报告见 [docs/project-report.md](docs/project-report.md)
- 技术架构图见 [docs/assets/07-technical-architecture.png](docs/assets/07-technical-architecture.png)

## 当前边界

- 这个仓库不是完整线上产品，而是“可运行 Demo + 方案展示”的作品集版本。
- 钉钉集成、知识库检索、风险词转介流程目前仍停留在方案设计或可继续扩展阶段。
- 如果继续打磨到更强的实习投递版本，下一步最值得补的是前端页面、对话记录存储和风险识别逻辑。
