# Zhiyuxing AI Assistant

[中文](README.md) | [English](README_EN.md)

Live demo after deployment: `https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Service-009688?logo=fastapi&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-145f66)](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
[![Release](https://img.shields.io/github/v/release/1420079678-ctrl/zhiyuxing-ai-assistant)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/tag/v0.1.0)
[![Stars](https://img.shields.io/github/stars/1420079678-ctrl/zhiyuxing-ai-assistant?style=social)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant)

Zhiyuxing AI Assistant is an AI-powered emotional support and study assistance service designed for college student scenarios. It focuses on high-frequency issues such as academic pressure, procrastination, exam anxiety, and interview stress, and responds with warm, concrete, actionable suggestions.

This repository is not just a concept showcase. It is structured as a runnable project foundation that can be used directly, extended further, and integrated with platforms such as DingTalk over time.

If this project is useful to you, consider giving it a `Star`.

## Quick Links

- `Try online`:[Live Demo](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
- `See release`:[v0.1.0 Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/tag/v0.1.0)
- `Chinese docs`:[README.md](README.md)
- `Model setup`:[docs/model-integration.en.md](docs/model-integration.en.md)
- `API reference`:[docs/api-reference.en.md](docs/api-reference.en.md)
- `Restricted public backend`:[docs/public-demo.md](docs/public-demo.md)

## What You Can Verify in 30 Seconds

- a public online demo instead of a repo that only has concept docs
- a runnable FastAPI + Web project instead of screenshots only
- a temporarily shareable restricted backend instead of local-only testing
- a practical repository with OpenAI / DeepSeek integration, local knowledge retrieval, session memory, and compatibility checks

Note:
the GitHub Pages demo is primarily a public preview of the UI and interaction flow. Full knowledge retrieval, session persistence, feedback recording, and real model calls are available when you run the backend locally.

## Why This Project

- Targets real and frequent student scenarios instead of generic chat.
- Combines emotional support with next-step study guidance in a single conversation loop.
- Supports local demo mode without any API key, so the repository can be started immediately.
- Keeps room for real model integration and DingTalk-based deployment scenarios.

## Core Capabilities

- `Supportive dialogue`: identifies expressions of stress, anxiety, and procrastination, then replies in a supportive tone.
- `Study action guidance`: breaks large tasks into small steps that are easier to start.
- `Local knowledge retrieval`: searches the built-in support and study guidance documents to enrich responses.
- `Custom knowledge document ingestion`: accepts additional Markdown or text documents through the API, giving the project a more extensible RAG-style entry point.
- `Session memory and persistence`: keeps recent turns, supports follow-up questions, and stores session data in local SQLite.
- `Risk detection and guardrail fallback`: switches to a fixed safety-oriented reply when high-risk expressions appear.
- `Dual runtime mode`: falls back to local demo mode when no model key is configured; switches to OpenAI-compatible model calls when configured.
- `Restricted public backend experience`: can open a temporary public tunnel so other people can try real backend endpoints.
- `Web service`: provides a browser-based UI, health check, runtime metadata endpoint, and Swagger docs.
- `Engineering basics`: includes tests, CI, environment variable examples, and supporting docs.

## Project Structure

```text
backend/
  api/            # route layer
  app_factory.py  # FastAPI assembly
  chat_logic.py   # prompts, styles, and demo reply logic
  chat_service.py # full chat pipeline
  config.py       # runtime config
  runtime.py      # provider resolution and compatibility checks
  schemas.py      # request/response models
services/
  knowledge.py    # retrieval and custom document writes
  safety.py       # risk detection
  storage.py      # SQLite persistence
static/           # web frontend
tests/            # regression tests
  api/            # API route and integration tests
  services/       # chat / runtime / safety / knowledge / storage unit tests
  conftest.py     # shared fixtures
```

## Use Cases

- Heavy academic workload with no clear starting point
- Long-term procrastination and difficulty getting started
- Persistent stress before exams, thesis defense, or interviews
- Emotional overload that disrupts study rhythm and execution

## Runtime Modes

| Mode | Description | Required Configuration |
| --- | --- | --- |
| Local demo mode | Uses built-in rules to generate supportive responses. Good for local preview, UI testing, and flow demos. | No API key required |
| Model mode | Calls an OpenAI-compatible API for real model responses. Good for validating real capabilities. | API key that matches the configured provider |

The project is designed so that it can run immediately after cloning. If no model key is configured, the page and `/chat` endpoint still return complete responses through demo mode.

## Screenshots

### Standalone Web Page

The default entry point in this repository is the standalone web page. It can run independently and does not require DingTalk to be opened.

![Web Page Preview](docs/assets/11-web-demo.png)

A public GitHub Pages demo is also included so visitors can try the interaction flow without configuring a backend or API keys:

- `https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

### DingTalk Integration Scenario

The following screenshots are kept as DingTalk integration examples to show how the project can later be connected to a collaboration platform.

![Platform Overview](docs/assets/09-platform-overview.png)

![Chat Demo](docs/assets/10-chat-demo.png)

## Tech Stack

- Python 3.13
- FastAPI
- OpenAI Python SDK
- Pydantic
- python-dotenv
- SQLite
- Markdown knowledge base
- Pytest
- GitHub Actions

## Architecture

![Technical Architecture](docs/assets/07-technical-architecture.png)

## Quick Start

Python 3.13 is recommended to stay aligned with the local dev environment and CI.

### Simplest Way To Start

If you just cloned the repository, enter the project root first:

```powershell
cd zhiyuxing-ai-assistant
```

If you just want to run the Web version first, use the repository launcher directly from the project root:

```powershell
.\start-web.ps1
```

Or double-click:

```text
start-web.bat
```

On first run, the script will automatically:

- create `.venv`
- install project dependencies
- copy `.env`
- check the current model configuration
- start the web service

To run tests, use:

```powershell
cd zhiyuxing-ai-assistant
.\run-tests.ps1
```

or double-click:

```text
run-tests.bat
```

### 1. Manual Dependency Setup (Advanced)

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2. One-Click Provider Setup

Use one of the setup scripts from the repository root:

```powershell
.\setup-openai.ps1
.\setup-deepseek-chat.ps1
.\setup-deepseek-r1.ps1
```

You can also double-click the matching `.bat` files. The scripts will:

- create `.env` from `.env.example` if it does not exist
- write the target `OPENAI_BASE_URL`, `MODEL_NAME`, and `MODEL_PROVIDER`
- set `MODEL_API_KEY_ENV` so the app reads the correct key variable first
- keep unrelated existing configuration

Important: these scripts only write provider presets. They do not remove the need for API keys.

- `.\setup-openai.ps1` configures the OpenAI preset and still requires `OPENAI_API_KEY`
- `.\setup-deepseek-chat.ps1` configures the DeepSeek Chat preset and still requires `DEEPSEEK_API_KEY`
- `.\setup-deepseek-r1.ps1` configures the DeepSeek R1 preset and still requires `DEEPSEEK_API_KEY`

If you run a setup script without a valid key, the project still starts, but it will fall back to local demo mode instead of calling an online model.

If you prefer manual setup, pay attention to:

- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`
- `MODEL_PROVIDER`
- `MODEL_API_KEY_ENV`
- `MODEL_TEMPERATURE`
- `DEMO_MODE`
- `CHAT_DB_PATH`

### 3. Run the Compatibility Check

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

This tells you:

- which key variable the current configuration will read
- whether the current model name and base URL look mismatched
- whether known compatibility rules such as `deepseek-reasoner` have been handled
- whether the current configuration is actually ready for real model calls

If you already filled in a real key, you can also run a small live probe:

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

This sends a minimal request to verify that the API is not only configured on paper, but actually callable by this project.

### 4. Start the Service

```bash
python -m uvicorn app:app --reload
```

If your system Python does not have the project dependencies installed, use the repository virtual environment directly:

```powershell
.\.venv\Scripts\python -m uvicorn app:app --reload
```

Or run the one-click launcher:

```powershell
.\start-web.ps1
```

Or double-click:

```text
start-web.bat
```

If you want to temporarily share the real backend with teachers, classmates, or interviewers, you can also start the restricted public demo:

```powershell
.\start-public-demo.ps1
```

This starts a dedicated backend instance and creates a temporary public tunnel. The terminal will print a public URL when it is ready. Important constraints:

- it forces `PUBLIC_DEMO_MODE=true`
- read endpoints such as `/chat`, `/api/meta`, and `/docs` stay accessible
- write endpoints such as `/api/knowledge/documents` and `/api/feedback` are blocked
- it is meant for public demo use and does not make real model calls
- the link only stays alive while your machine and the script keep running

See [docs/public-demo.md](docs/public-demo.md) for details.

After startup:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/meta`
- `http://127.0.0.1:8000/api/compatibility`
- `http://127.0.0.1:8000/api/knowledge/search?q=stress`
- `http://127.0.0.1:8000/api/session/<session_id>`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/project-docs/usage-guide.en.md`

### 5. Run Tests

```bash
python -m pytest -vv
```

Using the repository script is recommended because it avoids accidentally using the wrong Python environment:

```powershell
.\run-tests.ps1
```

Tests are now split by subsystem instead of being kept in a single file:

- `tests/api/test_api.py`
- `tests/services/test_chat_logic.py`
- `tests/services/test_runtime.py`
- `tests/services/test_knowledge.py`
- `tests/services/test_safety.py`
- `tests/services/test_storage.py`

You can also run the grouped suites explicitly:

```bash
python -m pytest tests/api tests/services -vv
```

## API Overview

- `GET /`: web page entry
- `POST /chat`: chat endpoint
- `GET /health`: health check
- `GET /api/meta`: runtime metadata
- `GET /api/compatibility`: model integration compatibility check
- `GET /api/knowledge/search`: local knowledge base search
- `GET /api/knowledge/documents`: list current knowledge documents
- `POST /api/knowledge/documents`: write a custom knowledge document
- `GET /api/session/{session_id}`: recent session history
- `POST /api/feedback`: mark a reply as helpful or needing more detail
- `GET /docs`: Swagger docs
- `GET /project-docs/...`: supporting project docs

### `POST /chat`

Example request:

```json
{
  "message": "I feel overwhelmed this week and cannot get myself to study.",
  "system_hint": "Keep the advice warm and actionable"
}
```

Example response:

```json
{
  "reply": "Your current state shows clear stress accumulation. Instead of trying to solve the whole week at once, shrink the task to the smallest next step, such as doing 20 minutes of review first.",
  "note": "Currently running in model mode. The response was generated by the configured OpenAI-compatible provider and enriched with recent session context and knowledge hits.",
  "mode": "openai",
  "session_id": "sess_xxxxxxxxxxxx",
  "assistant_message_id": 12,
  "memory_messages_used": 2,
  "knowledge_hits": [
    {
      "title": "Sleep and Recovery",
      "excerpt": "When stress has already started to affect sleep, combine short study blocks with offline support.",
      "source_path": "knowledge_base/04-sleep-and-recovery.md",
      "score": 3.8
    }
  ],
  "safety": {
    "level": "medium",
    "label": "Needs extra attention",
    "note": "Detected signs of insomnia, overwhelm, or exhaustion; offline support should be suggested.",
    "needs_human_support": true,
    "matched_keywords": ["can't sleep"]
  }
}
```

## Documentation

- Chinese:
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
- Other:
  [CONTRIBUTING.md](CONTRIBUTING.md)、
  [CHANGELOG.md](CHANGELOG.md)、
  [LICENSE](LICENSE)、
  [ROADMAP.md](ROADMAP.md)、
  [SECURITY.md](SECURITY.md)、
  [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)、
  [docs/github-launch-kit.md](docs/github-launch-kit.md)

## Roadmap

- improve crisis-expression detection and safer escalation behavior
- expand compatibility checks for more OpenAI-compatible providers
- improve multi-turn continuity and response quality
- expand the local knowledge base to more campus scenarios

## Integrating Different Models

The backend uses an OpenAI-compatible interface, so you can switch providers either by editing `.env` or by using the built-in setup scripts.

- Switch to OpenAI: run `.\setup-openai.ps1`
- Switch to DeepSeek Chat: run `.\setup-deepseek-chat.ps1`
- Switch to DeepSeek R1: run `.\setup-deepseek-r1.ps1`
- Switch to another OpenAI-compatible provider: run `scripts/setup_model_config.py` with a custom `base_url`, `model_name`, and `api_key_env`
- The web page supports selecting model target and counseling style directly
- The right-hand panel shows current provider, model, base URL, and compatibility status

Again, these scripts mean the project includes built-in presets for these providers. They do not mean those models can be called without API keys.

If you use `DeepSeek-R1`, the code already handles the `deepseek-reasoner` compatibility rule and avoids forcing the unsupported `temperature` parameter.

For official OpenAI and DeepSeek endpoints, this repository provides explicit support. For other "OpenAI-compatible" providers, full compatibility still depends on whether they really support Chat Completions, the current model naming convention, and common parameters. That is why the repository now includes a compatibility endpoint and a preflight check script.

## Safety Boundary

- The project is positioned as emotional support and study assistance, not professional diagnosis or treatment.
- The current implementation emphasizes gentle, concrete, and non-harmful replies.
- If a user expresses persistent insomnia, severe low mood, or self-harm risk, a real product should prioritize offline support and referral.

## DingTalk Integration Notes

- The web page is the default entry point for direct access and continued development.
- DingTalk is an optional business integration scenario and is not required for the project to run.
- If the current DingTalk integration is an `internal enterprise app`, it is usually only usable by members inside that organization and may also require admin authorization.
- In practice, this means external users normally cannot open the DingTalk version directly unless they join that organization or the app is redesigned for multi-organization / third-party distribution.
- If the goal is public accessibility, the web version should remain the primary entry point instead of treating DingTalk as the only access path.

## Testing and CI

- Local test command: `python -m pytest -vv`
- GitHub Actions is configured to run the base test suite after pushes
