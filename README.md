# 知愈星 AI Assistant

面向大学生场景的 AI 心理支持与学习辅助助手作品集项目，聚焦“情绪支持 + 学习建议”的联动式对话体验。

这个仓库的目标不是只展示一个想法，而是展示一套更适合实习投递的能力组合：

- AI 应用原型设计
- FastAPI 后端接口实现
- Prompt 约束与安全边界设计
- 独立 Web Demo 产品化
- 测试与 GitHub Actions 持续集成

## 项目概览

很多大学生面临的问题并不只是“不会学”，而是“在焦虑、拖延、自我怀疑的状态下无法进入学习”。知愈星尝试把情绪支持与学习建议放进同一个对话闭环里，而不是把二者拆成割裂的功能模块。

当前 GitHub 版本采用“可运行 Demo + 方案展示”的方式组织，既能直接运行，也能清晰体现项目思路、技术路径和工程边界。

## 为什么这个仓库适合投实习

### 能体现的工程能力

- `AI 应用落地`：基于 OpenAI Python SDK 实现对话接口，组织系统提示词、用户输入和补充要求。
- `后端开发`：使用 FastAPI 和 Pydantic 封装接口、请求体和响应体，具备基本服务化结构。
- `前端演示`：补充独立 Web Demo 页面，避免项目演示被平台权限绑死。
- `工程质量`：增加 pytest 测试和 GitHub Actions，保证基础功能可验证。
- `方案表达`：保留项目报告、架构图、流程图和集成边界说明，适合面试展开讲述。

### 能体现的产品思考

- 场景聚焦在大学生高频问题，而不是泛化聊天。
- 将“情绪识别 -> 学习建议 -> 行动拆解”作为核心闭环。
- 明确 AI 不是专业医疗替代，保留安全边界和转介意识。
- 区分“作品集演示入口”和“钉钉真实落地场景”，降低外部体验门槛。

## 当前已实现内容

- 一个可本地运行的 FastAPI 服务
- 一个独立 Web Demo 页面
- `/chat`、`/health`、`/api/meta` 等接口
- 适用于大学生场景的基础系统提示词约束
- 项目报告、流程图、架构图和钉钉权限说明文档
- `pytest` 测试
- GitHub Actions CI

## 当前边界

当前版本是作品集版本，不是完整线上产品。已经实现的部分和规划中的部分做了明确区分：

- 已实现：Demo 对话流程、接口、静态页面、文档整理、测试与 CI。
- 规划中：知识库检索、风险词识别与转介流程、对话记录存储、真实钉钉授权接入。

这种表达方式更适合实习投递，因为它既展示能力，也避免过度承诺。

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

## 架构与目录

技术架构图：

![技术架构图](docs/assets/07-technical-architecture.png)

项目目录：

```text
zhiyuxing-ai-assistant/
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── .python-version
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
    ├── resume-interview-guide.md
    └── assets/
```

## 快速启动

推荐使用 Python 3.13 运行本项目，以保持与当前本地开发和 CI 环境一致。

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
  "reply": "当前状态里明显存在压力堆积，可以先不追求一次解决整周问题，而是把任务缩小到今天最容易开始的一步，比如先完成 20 分钟复习。",
  "note": "这是作品集仓库中的最小可运行 Demo，用于展示项目方向与接口能力。"
}
```

## 实习投递辅助文档

- 项目报告：[docs/project-report.md](docs/project-report.md)
- 钉钉集成边界：[docs/dingtalk-integration.md](docs/dingtalk-integration.md)
- 简历与面试说明：[docs/resume-interview-guide.md](docs/resume-interview-guide.md)

## 钉钉集成边界

- 如果项目以钉钉企业内部应用形态部署，外部评审通常无法直接进入所属组织体验。
- 因此仓库默认提供独立 Web Demo 作为展示入口，钉钉版本作为业务落地场景保留在文档中说明。
- 这种拆分更适合作品集展示，也更便于说明平台集成与权限隔离问题。

## 测试与持续集成

```bash
python -m pytest -vv
```

仓库已配置 GitHub Actions，在推送后自动运行基础测试。
