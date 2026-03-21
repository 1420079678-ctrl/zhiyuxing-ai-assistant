# 知愈星 AI Assistant

知愈星是一个面向大学生场景的 AI 心理支持与学习辅助助手，围绕“情绪支持 + 学习指导”两条主线，尝试把共情式对话、行动建议和校园使用场景结合起来。

这个仓库适合用作实习作品集展示，因为它同时保留了两个层面：

- 一个可以本地运行、独立访问的 Web Demo；
- 一份完整整理过的项目方案文档、流程图和界面示意；
- 清晰体现了产品思考、接口设计、提示工程和安全边界意识。

## 项目亮点

- 场景聚焦：针对大学生常见的学业压力、社交焦虑、拖延和学习内耗设计对话方向。
- 双线联动：不是只做“心理安慰”，而是把情绪支持和学习建议做成一个连续闭环。
- 可运行展示：仓库提供 FastAPI + 原生前端页面，可直接接入 OpenAI 兼容模型进行对话测试。
- 伦理边界明确：回复中避免诊断化表达，对高风险场景保留转介意识，不把 AI 包装成专业医疗替代。
- 展示路径清晰：独立 Web Demo 不依赖评审进入你的钉钉组织即可体验。

## 当前仓库包含什么

- `app.py`：最小可运行服务，提供 Web Demo、健康检查和对话接口。
- `static/`：独立演示页的静态前端资源。
- `docs/project-report.md`：完整项目报告，包含定位、功能设计、创新点和技术方案。
- `docs/dingtalk-integration.md`：钉钉集成与权限边界说明。
- `docs/assets/`：流程图、架构图和界面示意图。
- `requirements.txt`：运行 Demo 所需依赖。
- `requirements-dev.txt`：测试和 CI 所需依赖。

## 技术栈

- Python
- FastAPI
- OpenAI Python SDK
- Pydantic
- python-dotenv
- Pytest
- GitHub Actions

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
├── requirements-dev.txt
├── .env.example
├── static/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── tests/
│   └── test_app.py
└── docs/
    ├── dingtalk-integration.md
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
pip install -r requirements.txt -r requirements-dev.txt
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
- `http://127.0.0.1:8000/api/meta`
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
- 钉钉集成与权限说明见 [docs/dingtalk-integration.md](docs/dingtalk-integration.md)
- 技术架构图见 [docs/assets/07-technical-architecture.png](docs/assets/07-technical-architecture.png)

## 钉钉权限边界

- 如果项目以钉钉企业内部应用形态部署，外部评审通常不能直接进入你的组织体验。
- 因此这个仓库默认提供独立 Web Demo 作为展示入口，钉钉版本作为业务落地场景保留在文档中说明。
- 面试时可以强调：你考虑了平台集成、权限隔离和作品集可访问性，而不是把演示绑死在个人租户里。

## 测试与持续集成

```bash
pytest
```

仓库已经补充了 `.github/workflows/ci.yml`，推送后会自动执行基础测试。

## 当前边界

- 这个仓库不是完整线上产品，而是“可运行 Demo + 方案展示”的作品集版本。
- 钉钉集成、知识库检索、风险词转介流程目前仍停留在方案设计或可继续扩展阶段。
- 如果继续打磨到更强的实习投递版本，下一步最值得补的是对话记录存储、风险识别逻辑和真实钉钉授权接入。
