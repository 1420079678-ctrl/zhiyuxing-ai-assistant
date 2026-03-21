# 使用说明

这份文档用于说明项目的运行方式、环境变量和常见问题，方便直接启动和继续开发。

## 运行模式

### 1. 本地演示模式

- 默认可用
- 不要求配置 `OPENAI_API_KEY`
- `/chat` 会返回内置的支持性建议
- 适合先验证页面、接口和整体流程

### 2. 模型调用模式

- 需要配置 `OPENAI_API_KEY`
- 可选配置 `OPENAI_BASE_URL` 和 `MODEL_NAME`
- `/chat` 会调用 OpenAI 兼容接口返回模型回复
- 适合继续验证真实模型能力

## 环境变量

可参考仓库根目录的 `.env.example`。

| 变量名 | 说明 | 是否必填 |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI 兼容接口密钥，留空时自动进入本地演示模式 | 否 |
| `OPENAI_BASE_URL` | OpenAI 兼容接口地址 | 否 |
| `MODEL_NAME` | 调用的模型名称 | 否 |
| `DEMO_MODE` | 设置为 `true` 时强制使用本地演示模式 | 否 |

## 本地启动

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

### 3. 启动服务

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
- `/docs`：Swagger 文档
- `/project-docs/dingtalk-integration.md`：钉钉接入说明

## 常见问题

### 为什么没配 API Key 也能返回结果？

因为项目默认支持本地演示模式。这样仓库拿下来后可以直接跑通流程，不会因为缺少密钥导致页面不可用。

### 为什么配置了 API Key 还是走本地演示模式？

检查 `.env` 中的 `DEMO_MODE` 是否被设置为 `true`。如果是，系统会优先使用本地演示模式。

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
