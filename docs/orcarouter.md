# OrcaRouter 接入指南

[中文](orcarouter.md) | [English](orcarouter.en.md)

OrcaRouter 是本项目的可选 OpenAI 兼容服务提供商。现有后端通过 `OPENAI_BASE_URL`、`MODEL_NAME` 和 `MODEL_API_KEY_ENV` 选择服务，无需更改对话接口。

## 1. 准备账号与密钥

通过 [项目推荐链接](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f) 或 [OrcaRouter 官网](https://www.orcarouter.ai/) 登录，在控制台创建供自己使用的 API Key。推荐链接可能为维护者带来推荐收益；服务是否可用及费用以你的账户和平台说明为准。

API 地址为 `https://api.orcarouter.ai/v1`。以下示例使用官方快速开始中的 `openai/gpt-4o-mini`；实际模型名应以你的账户可用模型或 `/v1/models` 为准。

## 2. 配置自托管后端

先按 [README](../README.md) 安装项目依赖并建立 `.venv`。在项目根目录运行以下命令；它先备份现有 `.env`，再复用仓库已有脚本写入配置：

```powershell
# Run from the project root after installing the project dependencies.
if (Test-Path -LiteralPath .env) {
  if (Test-Path -LiteralPath .env.before-orcarouter) {
    throw "Existing .env.before-orcarouter backup found; keep it safe before repeating this step."
  }
  Copy-Item -LiteralPath .env -Destination .env.before-orcarouter
}
.\.venv\Scripts\python scripts\setup_model_config.py `
  --preset openai `
  --provider-name OrcaRouter `
  --base-url https://api.orcarouter.ai/v1 `
  --model-name openai/gpt-4o-mini `
  --api-key-env ORCAROUTER_API_KEY `
  --demo-mode false
```

`--preset openai` 仅作为通用配置模板；后续参数会覆盖服务地址、展示名称、模型名和密钥变量，不会将 OrcaRouter Key 用于 OpenAI 官方地址。

首次交互运行时，脚本会提示输入 `ORCAROUTER_API_KEY`；该脚本使用普通终端输入，输入字符可见。也可以留空，随后在本地 `.env` 的 `ORCAROUTER_API_KEY=` 后填入自己的密钥。无需把真实密钥写进命令、README、截图或 GitHub。

确认本地 `.env` 中以下值正确，每个变量仅保留一个有效定义：

```dotenv
OPENAI_BASE_URL=https://api.orcarouter.ai/v1
MODEL_NAME=openai/gpt-4o-mini
MODEL_PROVIDER=OrcaRouter
MODEL_API_KEY_ENV=ORCAROUTER_API_KEY
ORCAROUTER_API_KEY=
DEMO_MODE=false
PUBLIC_DEMO_MODE=false
```

`ORCAROUTER_API_KEY=` 的空值需要在你自己的本地配置中补齐。上面的 `PUBLIC_DEMO_MODE=false` 也必须确认；配置脚本会保留此变量的原值。操作系统中已有的同名环境变量可能优先于 `.env`，遇到不符时先检查当前终端环境。

重启后端，在 Web 模型下拉框选择“当前配置（OrcaRouter / openai/gpt-4o-mini）”。选择独立的 OpenAI 或 DeepSeek 预设会使用对应官方服务；本指南不会新增一个独立的 OrcaRouter 下拉预设。

## 3. 验证配置与真实请求

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

检查输出中的提供商、API 地址、模型名和密钥变量。自定义 OpenAI 兼容地址的提示属于项目当前检查逻辑；配置检查通过不等于已成功调用远程模型。缺少密钥或启用任一演示模式时，不能视为真实接入成功。

填写有效密钥并确认账户可用后，可主动执行一次真实探测（会发送请求，可能产生模型费用）：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

只有看到“真实探测成功”及模型返回内容，并能在 OrcaRouter 请求记录中对应到该请求，才算完成端到端验证。GitHub Pages 静态演示和 `start-public-demo` 受限公开模式都不会据此自动变为真实模型调用。

## 4. 回滚与再次配置

备份文件含有原有配置，可能包含密钥，务必仅保存在本机。需要恢复时，在项目根目录执行并重启后端：

```powershell
if (-not (Test-Path -LiteralPath .env.before-orcarouter)) {
  throw "No pre-OrcaRouter configuration backup exists."
}
Copy-Item -LiteralPath .env.before-orcarouter -Destination .env -Force
```

如果原先没有 `.env`，可在本地将 `DEMO_MODE=true` 恢复为演示模式。重新配置时可再次运行通用配置脚本；先妥善保留已有备份，避免覆盖回滚依据。

## 合作与验证状态

2026-09-06 查看合作伙伴后台时：推广计划已批准、推荐链接已生效；开源目录仍待人工发布，应用标识尚未签发。本次提供的是 API Key 配置方式，没有实现 PKCE 登录或设备授权，也未验证真实 API 请求。目录收录、推广资格与 API 连接是独立状态，不能互相替代。

## 官方参考

- [Quickstart](https://docs.orcarouter.ai/getting-started/quickstart)
- [OpenAI SDK compatibility](https://docs.orcarouter.ai/compatibility/openai-sdk)
