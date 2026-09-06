# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [1.0.0] - 2026-09-06

### Major Commercial & Enterprise Transformation (大版本企业级重构)

#### Added
- **Production-Ready Deployment**: Multi-stage `Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml`, Nginx reverse proxy configuration with SSE tuning, and Kubernetes manifests (`deploy/k8s/deployment.yaml`).
- **Server-Sent Events (SSE) Streaming**: Added `POST /chat/stream` endpoint for real-time typewriter output across both live AI models and local demo modes.
- **Enterprise Observability**: Added standard Prometheus metrics endpoint (`GET /metrics`) tracking uptime, QPS, model invocations, guardrail triggers, and token estimates.
- **Request Tracing & Security**: Integrated `X-Request-ID` and `X-Response-Time` HTTP middleware, CORS support, and optional enterprise multi-tenant API Key authentication (`services/auth.py`).
- **Dual Business Scenarios**: Introduced **Enterprise EAP & Workplace Mode (企业员工关怀与职场抗压)** alongside **Campus Growth Mode (高校学业成长)**, with specialized prompts, topic detection, and actions.
- **Expanded Enterprise RAG Knowledge**: Added workplace burnout recovery (`06-workplace-burnout.md`) and career efficiency action (`07-career-efficiency-action.md`) knowledge documents, document deletion API (`DELETE /api/knowledge/documents/{id}`), and scenario filtering.
- **Multi-Session Management**: Added `GET /api/sessions` and `DELETE /api/sessions/{id}` APIs, and SQLite WAL mode optimization with connection timeout protections.
- **SaaS Copilot Console UI**: Completely redesigned `static/` web interface into an enterprise-grade AI Copilot workspace with multi-session drawer, real-time message stream bubbles, scenario switcher pills, live telemetry inspector, and knowledge base management modal.
- **Packaging & DevOps Automation**: Standardized `pyproject.toml` (PEP 621), `Makefile`, `deploy/scripts/deploy.sh`, and `.env.production`.
- **Commercialization Documentation**: Added Enterprise AI Copilot Whitepaper (`docs/commercialization.md`) and Docker production deployment manual (`docs/deployment-docker.md`).

#### Maintained
- Preserved 100% backward compatibility for existing REST endpoints (`/chat`, `/health`, `/api/meta`, etc.).
- Preserved all prior Git commits, release bundles, and historical version records.
- Preserved open-source MIT license, GitHub Pages demo, and active OrcaRouter partnership promotion program (elevated to recommended multi-model gateway).

## [0.7.0] - 2026-03-21

### Added

- local markdown knowledge base and retrieval endpoint
- custom knowledge document write and listing endpoints
- SQLite-backed session persistence and session history endpoint
- feedback recording endpoint for recent assistant replies
- rule-based risk detection with high-risk guardrail fallback
- restricted public backend demo mode with write protection and temporary tunnel launcher
- startup diagnostics via `doctor.ps1` and `doctor.bat`
- downloadable release package builder and release installation guides

### Improved

- refactored the backend into `backend/`, `api/`, and `services/` modules while keeping `app.py` as a compatible entrypoint
- web UI now shows session id, memory usage, risk level, knowledge hits, and recent history
- README and usage guides now distinguish public preview mode from full local backend capabilities
- test coverage now verifies knowledge retrieval, memory flow, high-risk handling, and feedback persistence
- tests are now split across `api` and `services` layers instead of a single file
- local startup and test commands now auto-create `.venv`, install dependencies, and reduce first-run friction
- release documentation now points users to packaged zip assets instead of raw source archives

## [0.1.0] - 2026-03-21

### Added

- runnable FastAPI web application with browser-based demo UI
- local demo mode that works without API keys
- provider presets for OpenAI, DeepSeek Chat, and DeepSeek R1
- compatibility preflight checks and optional live probe
- bilingual GitHub documentation in Chinese and English
- model target and counseling style selectors in the web UI

### Improved

- clarified API key requirements for provider setup scripts
- improved demo replies so they vary by topic and response style
- documented DingTalk integration as an optional scenario instead of a runtime dependency
