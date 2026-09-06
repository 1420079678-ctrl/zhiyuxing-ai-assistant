# Model Integration Guide

[中文](model-integration.md) | [English](model-integration.en.md)

This document explains how the web version connects to different models, why the DingTalk-based version can appear to "use a model directly", and how the local web project should be configured on its own.

## Summary

- the current web project uses the `OpenAI Python SDK`
- the backend talks through an `OpenAI-compatible` API
- if a provider supports the OpenAI Chat Completions interface, it can potentially be connected through `.env`
- the repository currently supports:
  - local demo mode
  - OpenAI-compatible model calls
  - both `OPENAI_API_KEY` and `DEEPSEEK_API_KEY`
  - `MODEL_API_KEY_ENV` to explicitly tell the project which key variable to use
  - one-click setup scripts and compatibility checks

## Why Can DingTalk Use a Model While the Local Web Project Still Needs Configuration?

If the DingTalk version can already call a model, that usually means the model credentials and provider binding have already been completed inside the DingTalk platform itself.

That does not mean the local FastAPI backend automatically inherits those platform-side settings.

The local web project is an independent backend, so it still needs to know:

- which model service to call
- which base URL to use
- which API key to use

So if `DeepSeek R1` works inside DingTalk, that does not automatically mean the local web service can call it without its own configuration.

## Current Configuration Variables

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | API key for OpenAI-compatible providers |
| `DEEPSEEK_API_KEY` | API key for DeepSeek |
| `OPENAI_BASE_URL` | API base URL |
| `MODEL_NAME` | model name |
| `MODEL_PROVIDER` | display name for the UI |
| `MODEL_API_KEY_ENV` | which key variable the current model should read first |
| `MODEL_TEMPERATURE` | temperature parameter, ignored for some models |
| `DEMO_MODE` | force local demo mode |

## Use Setup Scripts First

The repository provides three setup presets:

```powershell
.\setup-openai.ps1
.\setup-deepseek-chat.ps1
.\setup-deepseek-r1.ps1
```

The `.bat` files can also be used.

These scripts:

- initialize `.env`
- write the right `OPENAI_BASE_URL`
- write `MODEL_NAME`
- write `MODEL_PROVIDER`
- write `MODEL_API_KEY_ENV`
- preserve unrelated existing settings where possible

These scripts do not mean "no API key is needed".

They mean the repository includes built-in presets for these common provider combinations:

- `.\setup-openai.ps1`: writes the OpenAI preset, but real calls still need `OPENAI_API_KEY`
- `.\setup-deepseek-chat.ps1`: writes the DeepSeek Chat preset, but real calls still need `DEEPSEEK_API_KEY`
- `.\setup-deepseek-r1.ps1`: writes the DeepSeek R1 preset, but real calls still need `DEEPSEEK_API_KEY`

If no valid key is provided, the script can still finish successfully, but the service will only run in local demo mode.

If you want to configure another OpenAI-compatible provider, you can reuse the generic setup script:

```powershell
.\.venv\Scripts\python scripts\setup_model_config.py `
  --preset openai `
  --provider-name OpenAI-Compatible `
  --base-url https://your-provider.example.com/v1 `
  --model-name your-model-name `
  --api-key-env OPENAI_API_KEY `
  --api-key your_api_key
```

After that, run:

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

And if you already have a real key:

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

## Example Configurations

### 1. Local Demo Mode

```env
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=Local Demo
MODEL_API_KEY_ENV=OPENAI_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=true
```

### 2. OpenAI

```env
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=OpenAI
MODEL_API_KEY_ENV=OPENAI_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 3. DeepSeek Chat

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
MODEL_PROVIDER=DeepSeek
MODEL_API_KEY_ENV=DEEPSEEK_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 4. DeepSeek R1 / Reasoner

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-reasoner
MODEL_PROVIDER=DeepSeek
MODEL_API_KEY_ENV=DEEPSEEK_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

The code already handles `deepseek-reasoner` by skipping the `temperature` parameter when needed.

## What Does “Compatible” Mean in This Repository?

This boundary matters: not every provider that claims to be “OpenAI-compatible” is automatically fully compatible with this project.

The repository provides explicit support for:

- official OpenAI endpoints
- official DeepSeek endpoints

For other OpenAI-compatible services, “fully compatible” still depends on whether the provider really supports:

- Chat Completions
- the model name you configured
- the expected message format
- standard authentication headers
- common parameters such as `temperature`

That is why the current project uses three layers:

- `MODEL_API_KEY_ENV` to explicitly select the right key variable
- `/api/compatibility` and `scripts/check_model_config.py` for preflight validation
- model-specific compatibility rules such as the `deepseek-reasoner` temperature handling

This is more reliable than only claiming “supports OpenAI-compatible APIs” in a README.

## What the Web Page Shows

The current page already shows:

- current provider
- current model
- current API base URL
- current compatibility check result

The page also supports selecting:

- model target
- counseling style

So users can understand the current runtime setup without reading the code.

## Built-In Compatibility Handling

- falls back to local demo mode if no key is configured
- supports both `OPENAI_API_KEY` and `DEEPSEEK_API_KEY`
- reads the expected key via `MODEL_API_KEY_ENV`
- skips unsupported `temperature` for `deepseek-reasoner`
- includes setup scripts and a compatibility check endpoint

## References

- [DeepSeek API Quick Start](https://api-docs.deepseek.com/zh-cn/)
- [DeepSeek Models and Pricing](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
- [DeepSeek Reasoning Model Guide](https://api-docs.deepseek.com/guides/reasoning_model)

## OrcaRouter

Use the existing generic setup script to configure OrcaRouter as an OpenAI-compatible provider. See the [OrcaRouter guide](orcarouter.en.md) for the separate `ORCAROUTER_API_KEY`, endpoint, model ID, and live verification steps.
