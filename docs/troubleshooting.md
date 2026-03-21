# 启动排障

如果别人第一次运行这个项目时失败，优先不要手动乱改环境，先做这两步：

```powershell
cd zhiyuxing-ai-assistant
.\doctor.ps1
```

然后再启动：

```powershell
.\start-web.ps1
```

## `doctor.ps1` 会检查什么

- 当前是不是在项目根目录
- 机器上有没有可用的 Python 启动器
- `.venv` 能不能自动创建
- 依赖有没有安装完整
- `.env` 是否存在
- `8000` 端口是否被占用
- 当前模型配置能不能进入真实调用模式

## 最常见的失败原因

### 1. 不在项目目录里

错误示例：

```powershell
C:\Users\xxx> python -m pytest -vv
```

这种情况下用的是系统 Python，而且通常不在仓库目录里。

正确方式：

```powershell
cd zhiyuxing-ai-assistant
.\run-tests.ps1
```

### 2. 本机没有 Python

现象：

- `py` 或 `python` 命令不存在
- `doctor.ps1` 会直接报 `No usable Python launcher found`

处理：

- 安装 Python 3.13
- 安装时勾选加入 PATH

### 3. 端口 8000 被占用

现象：

- `start-web.ps1` 启动时提示地址已被占用

处理：

- 关闭本机占用 `8000` 端口的其他服务
- 或自行改用其他端口启动 `uvicorn`

### 4. 想用真实模型，但没有 API Key

现象：

- 兼容性检查会给出 warning
- 但项目依然可以启动

处理：

- 不填 Key 时，项目默认回退到 demo mode
- 如果要真实模型调用，再按 [docs/model-integration.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/model-integration.md) 配置

## 给别人最推荐的运行方式

只需要发这两条：

```powershell
cd zhiyuxing-ai-assistant
.\start-web.ps1
```

如果失败，再补一条：

```powershell
.\doctor.ps1
```
