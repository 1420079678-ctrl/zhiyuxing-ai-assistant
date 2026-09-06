# 知愈星 AI Assistant

[中文](README.md) | [English](README_EN.md)

在线 Demo（部署后）：`https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Service-009688?logo=fastapi&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-145f66)](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
[![Release](https://img.shields.io/github/v/release/1420079678-ctrl/zhiyuxing-ai-assistant)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)
[![Stars](https://img.shields.io/github/stars/1420079678-ctrl/zhiyuxing-ai-assistant?style=social)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant)

面向大学生场景的 AI 情绪支持与学习辅助服务，围绕学业压力、拖延内耗、考试与面试焦虑等高频问题，提供温和、具体、可执行的支持性建议。

这个仓库的目标不是单纯展示方案，而是提供一个可以直接运行、便于继续开发、也能逐步接入钉钉等平台的完整项目基础。

如果这个项目对你有帮助，欢迎点一个 `Star`。

## OrcaRouter 可选模型接入

[![OrcaRouter 可选提供商](https://img.shields.io/badge/OrcaRouter-Optional_provider-2563eb)](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f)

可通过项目已有的 OpenAI 兼容配置接入 OrcaRouter，在自托管后端中使用其模型服务。详见 [OrcaRouter 接入指南](docs/orcarouter.md)，包含可重放配置命令、密钥设置、验证和回滚步骤。

- [前往 OrcaRouter](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f) · [官方快速开始](https://docs.orcarouter.ai/getting-started/quickstart)
- 上述链接为项目推荐链接；通过该链接使用服务，维护者可能获得推荐收益。
- 状态记录（2026-09-06）：推广计划已生效；开源目录尚未发布，应用标识尚未签发。本文提供配置接入方式，尚未完成真实 API 调用验证，不代表官方背书。
- GitHub Pages 演示仍使用本地演示逻辑；真实调用需自行配置后端和 API Key。

## 快速入口

- `在线体验`：[Live Demo](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
- `下载发布包`：[Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)
- `英文说明`：[README_EN.md](README_EN.md)
- `模型接入`：[docs/model-integration.md](docs/model-integration.md)
- `API 参考`：[docs/api-reference.md](docs/api-reference.md)
- `受限公开后端`：[docs/public-demo.md](docs/public-demo.md)
- `启动排障`：[docs/troubleshooting.md](docs/troubleshooting.md)
- `Release 安装`：[docs/release-install.md](docs/release-install.md)

## 30 秒能看到什么

- 一个可直接打开的在线 Demo，而不是只停留在方案文档
- 一个可本地运行的 FastAPI + Web 项目，而不是只有截图
- 一个可临时公开访问的受限后端，而不是只能在本机自测
- 一个支持 OpenAI / DeepSeek 接入、知识检索、会话记忆和兼容性检查的工程化仓库

说明：
GitHub Pages 上的在线 Demo 主要用于公开展示页面和交互流程；完整的知识库检索、会话持久化、反馈记录和真实模型调用，需要按下文步骤本地启动后端。

## 项目价值

- 聚焦真实且高频的大学生使用场景，而不是泛化聊天。
- 把“情绪支持”和“学习行动建议”放进同一轮对话，形成更完整的支持闭环。
- 支持无密钥运行的本地演示模式，拿到仓库后可以直接启动和体验。
- 预留模型调用和钉钉集成空间，便于后续继续做成更完整的产品。

## 核心能力

- `情绪支持对话`：识别压力、焦虑、拖延等常见表达，给出温和回应。
- `学习行动建议`：把大问题拆成可立刻执行的小步骤，降低启动门槛。
- `本地知识库检索`：根据问题检索内置心理支持与学习建议文档片段，增强回复内容。
- `自定义知识文档接入`：可通过 API 把自定义 Markdown / 文本写入知识库，形成更像 RAG 项目的可扩展入口。
- `会话记忆与持久化`：自动记录最近对话，支持继续追问、查看历史和本地 SQLite 持久化。
- `风险识别与转介兜底`：遇到高风险表达时优先切换固定安全回复，而不是继续普通对话。
- `双运行模式`：未配置模型密钥时使用本地演示模式；配置后切换到 OpenAI 兼容模型调用模式。
- `受限公开后端体验`：可一键启动临时公网隧道，让他人直接访问真实后端接口进行体验。
- `Web 服务化`：提供可直接访问的页面、健康检查、接口元信息和 Swagger 文档。
- `工程基础`：包含测试、CI、环境变量说明和补充文档。

## 工程结构

```text
backend/
  api/            # 路由层
  app_factory.py  # FastAPI 应用装配
  chat_logic.py   # 提示词、风格和 Demo 回复逻辑
  chat_service.py # 完整对话流程
  config.py       # 运行配置
  runtime.py      # 模型解析与兼容性检查
  schemas.py      # 请求/响应模型
services/
  knowledge.py    # 知识检索与自定义文档写入
  safety.py       # 风险检测
  storage.py      # SQLite 会话持久化
static/           # Web 前端
tests/            # 回归测试
  api/            # API 路由与集成测试
  services/       # chat / runtime / safety / knowledge / storage 单元测试
  conftest.py     # 统一测试夹具
```

## 使用场景

- 学业压力大，任务很多，不知道从哪里开始
- 长期拖延，明知道该做但迟迟启动不了
- 考试、答辩、面试前持续紧张，难以进入准备状态
- 情绪混乱导致学习节奏失序，需要先稳定状态再恢复行动

## 运行模式

| 模式 | 说明 | 需要的配置 |
| --- | --- | --- |
| 本地演示模式 | 使用内置规则生成支持性回复，适合本地启动、调试界面和展示流程 | 无需 API Key |
| 模型调用模式 | 调用 OpenAI 兼容接口生成回复，适合继续做真实能力验证 | 与当前模型匹配的 API Key |

项目默认优先保证“拿到就能跑”。如果没有配置模型密钥，页面和 `/chat` 接口仍然可以完整返回结果。

## 页面预览

### 独立 Web 页面

当前仓库默认运行的是独立 Web 页面，不需要打开钉钉即可访问和体验。

![Web 页面预览](docs/assets/11-web-demo.png)

也提供基于 GitHub Pages 的公开在线演示页，方便在不配置后端和 API Key 的情况下直接体验交互流程：

- `https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

### 钉钉接入场景示意

下面两张图保留为钉钉平台接入场景示意，用于说明项目后续可以如何落到企业协同平台中。

![平台界面示意](docs/assets/09-platform-overview.png)

![对话界面示意](docs/assets/10-chat-demo.png)

## 技术栈

- Python 3.13
- FastAPI
- OpenAI Python SDK
- Pydantic
- python-dotenv
- SQLite
- Markdown Knowledge Base
- Pytest
- GitHub Actions

## 架构图

![技术架构图](docs/assets/07-technical-architecture.png)

## 快速启动

推荐使用 Python 3.13，以保持与当前本地开发和 CI 环境一致。

### Release 压缩包安装

如果你不想 clone 仓库，也不想手动配 Git，最省事的方式是直接下载 Release 压缩包：

- [Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)

优先下载：

- `zhiyuxing-ai-assistant-release-v*.zip`

这类压缩包里会额外包含：

- `start-web.bat`
- `doctor.bat`
- `INSTALL.txt`

完整说明见：[docs/release-install.md](docs/release-install.md)

### 最简单启动方式

如果你是刚 clone 下来，先进入项目根目录：

```powershell
cd zhiyuxing-ai-assistant
```

如果你只是想先把 Web 版跑起来，不想手动配虚拟环境，直接在项目根目录运行：

```powershell
.\start-web.ps1
```

或者直接双击：

```text
start-web.bat
```

首次运行时，脚本会自动：

- 创建 `.venv`
- 安装项目依赖
- 自动复制 `.env`
- 检查当前模型接入配置
- 启动 Web 服务

如果别人第一次运行失败，先不要手动折腾环境，直接运行：

```powershell
.\doctor.ps1
```

或双击：

```text
doctor.bat
```

这个脚本会自动检查：

- 是否在项目根目录
- Python 是否安装
- `.venv` 和依赖是否能自动补齐
- `8000` 端口是否被占用
- 当前模型配置是否只能走 demo mode

要跑测试也不需要自己记命令，直接运行：

```powershell
cd zhiyuxing-ai-assistant
.\run-tests.ps1
```

或双击：

```text
run-tests.bat
```

### 1. 手动安装依赖（进阶）

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2. 一键配置模型接入

推荐直接使用仓库根目录下一键脚本：

```powershell
.\setup-openai.ps1
.\setup-deepseek-chat.ps1
.\setup-deepseek-r1.ps1
```

也可以双击对应的 `.bat` 文件。脚本会自动：

- 不存在 `.env` 时，从 `.env.example` 复制一份
- 按目标模型写入 `OPENAI_BASE_URL`、`MODEL_NAME`、`MODEL_PROVIDER`
- 自动设置 `MODEL_API_KEY_ENV`，确保项目优先读取正确的密钥变量
- 保留其他未切换的配置项

需要注意：这几个脚本只是帮你一键写好模型接入配置，不是免 API Key 调用。

- `.\setup-openai.ps1` 对应 OpenAI 官方接口，真实调用需要 `OPENAI_API_KEY`
- `.\setup-deepseek-chat.ps1` 对应 DeepSeek Chat，真实调用需要 `DEEPSEEK_API_KEY`
- `.\setup-deepseek-r1.ps1` 对应 DeepSeek R1，真实调用也需要 `DEEPSEEK_API_KEY`

如果运行脚本时没有填写对应 Key，项目仍然可以启动，但会自动回退到本地演示模式，不会真的调用线上模型。

如果想手动配置，至少需要关注：

- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`
- `MODEL_PROVIDER`
- `MODEL_API_KEY_ENV`
- `MODEL_TEMPERATURE`
- `DEMO_MODE`
- `CHAT_DB_PATH`

### 3. 启动前检查兼容性

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

这个检查会直接告诉你：

- 当前到底会读取哪个密钥变量
- 当前模型和 API 地址是否存在明显错配
- `deepseek-reasoner` 这类模型是否已经按兼容规则处理
- 当前配置是否真的可以进入真实模型调用模式

如果你已经填了真实 Key，还可以追加一次最小真实探测：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

这一步会实际发起一次极小请求，用来确认“不是看起来兼容，而是真的能调通”。

### 4. 启动服务

```bash
python -m uvicorn app:app --reload
```

如果你的系统 Python 没装项目依赖，最稳的方式是直接使用仓库自带虚拟环境：

```powershell
.\.venv\Scripts\python -m uvicorn app:app --reload
```

也可以直接运行仓库根目录下的一键脚本：

```powershell
.\start-web.ps1
```

或双击：

```text
start-web.bat
```

如果你想把“真实后端”临时分享给老师、同学或面试官，也可以启动受限公开演示：

```powershell
.\start-public-demo.ps1
```

这个脚本会自动启动一个专用后端并建立临时公网隧道，终端里会打印一个可直接访问的公开 URL。需要注意：

- 它会强制启用 `PUBLIC_DEMO_MODE=true`
- `/chat`、`/api/meta`、`/docs` 等读接口可访问
- `/api/knowledge/documents` 与 `/api/feedback` 等写接口会被禁止
- 它只适合公开演示，不会发起真实模型调用
- 链接只在你的电脑和脚本持续运行时有效

更完整说明见：[docs/public-demo.md](docs/public-demo.md)

启动后可访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/meta`
- `http://127.0.0.1:8000/api/compatibility`
- `http://127.0.0.1:8000/api/knowledge/search?q=失眠`
- `http://127.0.0.1:8000/api/session/<session_id>`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/project-docs/usage-guide.md`

### 5. 运行测试

```bash
python -m pytest -vv
```

更推荐直接使用仓库脚本，这样不会误用系统 Python：

```powershell
.\run-tests.ps1
```

当前测试已经按子系统拆分，不再集中在单个文件里：

- `tests/api/test_api.py`
- `tests/services/test_chat_logic.py`
- `tests/services/test_runtime.py`
- `tests/services/test_knowledge.py`
- `tests/services/test_safety.py`
- `tests/services/test_storage.py`

如果只想针对某个层级回归，也可以这样运行：

```bash
python -m pytest tests/api tests/services -vv
```

## 接口概览

- `GET /`：Web 页面入口
- `POST /chat`：对话接口
- `GET /health`：服务健康检查
- `GET /api/meta`：服务元信息与当前运行模式
- `GET /api/compatibility`：模型接入兼容性检查
- `GET /api/knowledge/search`：本地知识库检索
- `GET /api/knowledge/documents`：列出当前知识文档
- `POST /api/knowledge/documents`：写入自定义知识文档
- `GET /api/session/{session_id}`：最近会话记录
- `POST /api/feedback`：对回复提交有帮助 / 需要更具体的反馈
- `GET /docs`：Swagger 文档
- `GET /project-docs/...`：项目补充文档

### `POST /chat`

请求示例：

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
  "note": "当前为模型调用模式。回复由配置的 OpenAI 兼容接口生成，并结合了最近会话与知识库片段。",
  "mode": "openai",
  "session_id": "sess_xxxxxxxxxxxx",
  "assistant_message_id": 12,
  "memory_messages_used": 2,
  "knowledge_hits": [
    {
      "title": "考试压力与恢复",
      "excerpt": "当考试焦虑已经影响睡眠时，建议同时安排线下支持和短时复习块。",
      "source_path": "knowledge_base/04-sleep-and-recovery.md",
      "score": 3.8
    }
  ],
  "safety": {
    "level": "medium",
    "label": "需要额外关注",
    "note": "检测到持续失眠、崩溃或明显耗竭相关表达，建议尽快联系线下支持资源。",
    "needs_human_support": true,
    "matched_keywords": ["失眠"]
  }
}
```

## 文档入口

- 中文：
  [docs/api-reference.md](docs/api-reference.md)、
  [docs/project-report.md](docs/project-report.md)、
  [docs/usage-guide.md](docs/usage-guide.md)、
  [docs/model-integration.md](docs/model-integration.md)、
  [docs/dingtalk-integration.md](docs/dingtalk-integration.md)
- English:
  [docs/api-reference.en.md](docs/api-reference.en.md)、
  [docs/project-report.en.md](docs/project-report.en.md)、
  [docs/usage-guide.en.md](docs/usage-guide.en.md)、
  [docs/model-integration.en.md](docs/model-integration.en.md)、
  [docs/dingtalk-integration.en.md](docs/dingtalk-integration.en.md)
- 其他：
  [CONTRIBUTING.md](CONTRIBUTING.md)、
  [CHANGELOG.md](CHANGELOG.md)、
  [LICENSE](LICENSE)、
  [ROADMAP.md](ROADMAP.md)、
  [SECURITY.md](SECURITY.md)、
  [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)、
  [docs/github-launch-kit.md](docs/github-launch-kit.md)

## 路线图

- 继续增强危机表达识别和更安全的引导边界
- 继续扩展更多 OpenAI 兼容供应商的兼容检查
- 增强多轮对话连续性与回复稳定性
- 将本地知识库扩展到更多高校场景

## 接入不同大模型

当前项目后端使用的是 OpenAI 兼容接口，因此可以通过修改 `.env` 或直接运行一键脚本切换不同模型提供商。

- 切到 OpenAI：运行 `.\setup-openai.ps1`
- 切到 DeepSeek Chat：运行 `.\setup-deepseek-chat.ps1`
- 切到 DeepSeek R1：运行 `.\setup-deepseek-r1.ps1`
- 切到其他 OpenAI 兼容供应商：运行 `scripts/setup_model_config.py` 并传入自定义 `base_url`、`model_name`、`api_key_env`
- Web 页面支持直接下拉选择模型目标和辅导风格
- 页面右侧会直接显示当前提供商、当前模型、API 地址和接入兼容检查结果

再次强调：这些脚本表示“项目已内置这些接入预设”，不是“这几个模型可以不填 Key 直接调用”。

如果要接 `DeepSeek-R1`，当前代码已经处理了 `deepseek-reasoner` 的参数兼容问题，不会再强行传不适合的 `temperature` 参数。

需要说明的是：本项目对 `OpenAI` 和 `DeepSeek` 官方接口可以做到明确兼容；对其他“OpenAI 兼容”供应商，是否完全兼容仍取决于对方是否真的支持 Chat Completions、当前模型名和常用参数格式。仓库里新增的兼容检查接口和脚本，就是用来把这件事提前说明白，而不是等运行时报错。

## 安全边界

- 项目定位是情绪支持和学习辅助，不替代专业心理诊断或治疗。
- 当前实现强调温和、具体、避免危险引导的回复风格。
- 如果用户出现持续失眠、严重低落或自伤相关表达，实际产品应优先引导线下求助与转介。

## 钉钉接入说明

- Web 页面是默认入口，便于直接访问和继续开发。
- 钉钉是可选的真实业务接入场景，不影响项目本身独立运行。
- 如果当前接的是钉钉`企业内部应用`，通常只有该组织内成员才能在钉钉里使用，往往还需要管理员授权。
- 这意味着别人一般不能“直接打开你的钉钉版就用”，除非他加入该组织，或你把应用做成多组织分发 / 第三方应用。
- 如果目标是让任何人都能直接体验，这个项目应以 Web 版为主入口，而不是把钉钉端当成唯一入口。

## 测试与持续集成

- 本地测试命令：`python -m pytest -vv`
- 仓库已配置 GitHub Actions，在推送后自动运行基础测试
