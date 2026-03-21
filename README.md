# 知愈星 AI Assistant

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Service-009688?logo=fastapi&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)

面向大学生场景的 AI 情绪支持与学习辅助服务，围绕学业压力、拖延内耗、考试与面试焦虑等高频问题，提供温和、具体、可执行的支持性建议。

这个仓库的目标不是单纯展示方案，而是提供一个可以直接运行、便于继续开发、也能逐步接入钉钉等平台的完整项目基础。

## 项目价值

- 聚焦真实且高频的大学生使用场景，而不是泛化聊天。
- 把“情绪支持”和“学习行动建议”放进同一轮对话，形成更完整的支持闭环。
- 支持无密钥运行的本地演示模式，拿到仓库后可以直接启动和体验。
- 预留模型调用和钉钉集成空间，便于后续继续做成更完整的产品。

## 核心能力

- `情绪支持对话`：识别压力、焦虑、拖延等常见表达，给出温和回应。
- `学习行动建议`：把大问题拆成可立刻执行的小步骤，降低启动门槛。
- `双运行模式`：未配置模型密钥时使用本地演示模式；配置后切换到 OpenAI 兼容模型调用模式。
- `Web 服务化`：提供可直接访问的页面、健康检查、接口元信息和 Swagger 文档。
- `工程基础`：包含测试、CI、环境变量说明和补充文档。

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

启动后可访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/meta`
- `http://127.0.0.1:8000/api/compatibility`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/project-docs/usage-guide.md`

### 5. 运行测试

```bash
python -m pytest -vv
```

## 接口概览

- `GET /`：Web 页面入口
- `POST /chat`：对话接口
- `GET /health`：服务健康检查
- `GET /api/meta`：服务元信息与当前运行模式
- `GET /api/compatibility`：模型接入兼容性检查
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
  "note": "当前为模型调用模式。回复由配置的 OpenAI 兼容接口生成。",
  "mode": "openai"
}
```

## 文档入口

- [docs/project-report.md](docs/project-report.md)：完整项目报告与方案背景
- [docs/usage-guide.md](docs/usage-guide.md)：运行模式、环境变量和常见问题说明
- [docs/model-integration.md](docs/model-integration.md)：不同大模型的接入方式与 `.env` 配置示例
- [docs/dingtalk-integration.md](docs/dingtalk-integration.md)：钉钉权限模型与集成边界说明

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
- 如果接入钉钉，需要根据企业内部应用、多组织分发或用户授权模式处理权限问题。

## 测试与持续集成

- 本地测试命令：`python -m pytest -vv`
- 仓库已配置 GitHub Actions，在推送后自动运行基础测试
