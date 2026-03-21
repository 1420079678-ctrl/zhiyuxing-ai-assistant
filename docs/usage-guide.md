# 使用说明

[中文](usage-guide.md) | [English](usage-guide.en.md)

这份文档用于说明项目的运行方式、环境变量和常见问题，方便直接启动和继续开发。

## 运行模式

### 1. 本地演示模式

- 默认可用
- 不要求配置 `OPENAI_API_KEY`
- `/chat` 会返回内置的支持性建议
- 适合先验证页面、接口和整体流程

### 2. 模型调用模式

- 需要配置与当前模型匹配的密钥变量
- 支持 `OPENAI_API_KEY`
- 也支持 `DEEPSEEK_API_KEY`
- 可选配置 `OPENAI_BASE_URL`、`MODEL_NAME`、`MODEL_PROVIDER`、`MODEL_API_KEY_ENV`
- `/chat` 会调用 OpenAI 兼容接口返回模型回复
- 适合继续验证真实模型能力

## 环境变量

可参考仓库根目录的 `.env.example`。

| 变量名 | 说明 | 是否必填 |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI 兼容接口密钥，留空时自动进入本地演示模式 | 否 |
| `DEEPSEEK_API_KEY` | DeepSeek 密钥，未设置 `OPENAI_API_KEY` 时会回退使用 | 否 |
| `OPENAI_BASE_URL` | OpenAI 兼容接口地址 | 否 |
| `MODEL_NAME` | 调用的模型名称 | 否 |
| `MODEL_PROVIDER` | 页面展示用的提供商名称，例如 `OpenAI` / `DeepSeek` | 否 |
| `MODEL_API_KEY_ENV` | 当前模型优先读取哪个密钥变量，例如 `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` | 否 |
| `MODEL_TEMPERATURE` | 温度参数 | 否 |
| `DEMO_MODE` | 设置为 `true` 时强制使用本地演示模式 | 否 |

## 本地启动

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2. 一键配置模型

优先推荐直接运行一键脚本：

```powershell
.\setup-openai.ps1
.\setup-deepseek-chat.ps1
.\setup-deepseek-r1.ps1
```

也可以双击对应的 `.bat` 文件。

这些脚本会自动：

- 初始化 `.env`
- 写入当前模型所需的 `OPENAI_BASE_URL`
- 写入 `MODEL_NAME`、`MODEL_PROVIDER`
- 自动设置 `MODEL_API_KEY_ENV`
- 尽量保留现有密钥和其他环境变量

这几个脚本不是免 Key 调用，只是把模型接入配置一次写好：

- `.\setup-openai.ps1`：真实调用需要 `OPENAI_API_KEY`
- `.\setup-deepseek-chat.ps1`：真实调用需要 `DEEPSEEK_API_KEY`
- `.\setup-deepseek-r1.ps1`：真实调用需要 `DEEPSEEK_API_KEY`

如果你没有填写对应 Key，项目也不会坏掉，只是会继续运行在本地演示模式。

### 3. 手动配置环境变量

```powershell
Copy-Item .env.example .env
```

### 4. 启动前检查

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

它会检查：

- 当前模型会读取哪个 API Key
- 当前 `.env` 是否真的能进入真实模型调用模式
- 当前 `OPENAI_BASE_URL` 和 `MODEL_NAME` 是否存在明显错配
- `deepseek-reasoner` 的参数兼容规则是否已处理

如果已经配置了真实密钥，还可以继续执行：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

这会实际发起一次最小模型请求，用来验证当前 API 是否真的能被本项目正常调用。

### 5. 启动服务

```bash
python -m uvicorn app:app --reload
```

如果系统环境里缺少依赖，优先使用仓库虚拟环境：

```powershell
.\.venv\Scripts\python -m uvicorn app:app --reload
```

也可以直接运行：

```powershell
.\start-web.ps1
```

或者双击根目录的 `start-web.bat`。

## 常用地址

- `/`：Web 页面入口
- `/chat`：对话接口
- `/health`：健康检查
- `/api/meta`：服务元信息与当前运行模式
- `/api/compatibility`：模型接入兼容检查
- `/docs`：Swagger 文档
- `/project-docs/model-integration.md`：不同模型接入说明
- `/project-docs/dingtalk-integration.md`：钉钉接入说明

## 常见问题

### 为什么没配 API Key 也能返回结果？

因为项目默认支持本地演示模式。这样仓库拿下来后可以直接跑通流程，不会因为缺少密钥导致页面不可用。

### 一键脚本是不是代表不用 API Key？

不是。一键脚本只是把 `.env` 写成对应模型的推荐配置。

- OpenAI 预设仍然需要 `OPENAI_API_KEY`
- DeepSeek 预设仍然需要 `DEEPSEEK_API_KEY`

如果 Key 留空，项目会自动回退到本地演示模式，所以页面仍然能返回内容，但那不是线上模型真实回复。

### 为什么配置了 API Key 还是走本地演示模式？

先检查 `.env` 中的 `DEMO_MODE` 是否被设置为 `true`。如果是，系统会优先使用本地演示模式。

再检查当前模型是不是在读取正确的密钥变量。现在项目会优先按 `MODEL_API_KEY_ENV` 读取密钥，而不是只看有没有任意一个 Key。最稳的方式是直接运行：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

### 为什么明明填了 `OPENAI_API_KEY`，切到 DeepSeek 还是可能失败？

因为 DeepSeek 默认应读取 `DEEPSEEK_API_KEY`，而不是只要有任意一个 Key 就算配置完成。

当前项目已经补上了这层判断：

- 切到 OpenAI 时，会优先读取 `OPENAI_API_KEY`
- 切到 DeepSeek 时，会优先读取 `DEEPSEEK_API_KEY`
- 如果你接的是其他 OpenAI 兼容供应商，可以手动设置 `MODEL_API_KEY_ENV`

### 为什么系统环境里跑 `python -m pytest` 失败？

通常是因为全局 Python 没安装测试依赖。优先使用仓库虚拟环境中的解释器，例如：

```bash
.\.venv\Scripts\python -m pytest -q
```

### 为什么运行 `python -m uvicorn app:app --reload` 会报错？

如果报错类似 `No module named uvicorn`，说明你用的是系统 Python，而不是项目虚拟环境。请改用：

```powershell
.\.venv\Scripts\python -m uvicorn app:app --reload
```

或者直接运行 `start-web.ps1` / `start-web.bat`。

### 钉钉是不是必须项？

不是。当前项目可以作为独立 Web 服务运行，钉钉是可选的接入场景。

### 如何接入 DeepSeek R1 这类不同模型？

项目使用的是 OpenAI 兼容接口方式。只要修改 `.env` 中的 `OPENAI_BASE_URL`、`MODEL_NAME`、`MODEL_API_KEY_ENV` 和对应密钥，就可以切换不同模型提供商。详细示例见：

- [model-integration.md](model-integration.md)
