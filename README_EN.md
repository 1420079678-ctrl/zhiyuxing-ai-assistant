# Zhiyuxing AI Assistant (ZhiYuXing Copilot)

[中文](README.md) | [English](README_EN.md)

Live demo after deployment: `https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

![Version 1.0.0](https://img.shields.io/badge/Release-v1.0.0--Enterprise-blue.svg)
![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Service-009688?logo=fastapi&logoColor=white)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Stars](https://img.shields.io/github/stars/1420079678-ctrl/zhiyuxing-ai-assistant?style=social)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant)

**Zhiyuxing AI Assistant (ZhiYuXing Copilot)** is an enterprise-grade AI copilot platform for mental health support, emotional resilience, and micro-action empowerment. Rather than generic chit-chat, the platform delivers structured emotional containment, domain-specific RAG knowledge retrieval, rule-based risk guardrails, and executable micro-action steps across two primary commercial pillars: **Enterprise EAP & Workplace Well-being** and **Campus & Higher-Ed Academic Growth**.

The platform is fully production-ready with **industrial containerized deployments** (Docker, Docker Compose, Nginx reverse proxy with SSE tuning, Kubernetes manifests), **Server-Sent Events (SSE) streaming (`POST /chat/stream`)**, and **Prometheus observability (`GET /metrics`)**, while preserving zero-key local demo modes for friction-free evaluation.

If this project is useful to you, consider giving it a `Star` ⭐.

---

## 🌟 Recommended Multi-Model Gateway: OrcaRouter

[![OrcaRouter Recommended Gateway](https://img.shields.io/badge/OrcaRouter-Recommended_Gateway-2563eb)](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f)

In production environments requiring multi-model resilience and load distribution, integrate OrcaRouter using the project's native OpenAI-compatible configuration:

- [Open OrcaRouter](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f) · [Official Quickstart](https://docs.orcarouter.ai/getting-started/quickstart) · [Project Integration Guide](docs/orcarouter.en.md)
- Above link is the project's referral link; maintainers may earn referral revenue when services are utilized.
- Status recorded on 2026-09-06: the referral program is active; configuration instructions are verified and ready.
- The GitHub Pages demo continues to run local browser demo logic; live model invocation requires configuring API keys.

---

## 🚀 Dual Commercial Scenarios

| Scenario | Target Pain Points | Output & Empowerment |
|---|---|---|
| 🏢 **Enterprise EAP & Workplace** | High delivery stress, burnout, emotional exhaustion, cross-team alignment friction | 5-minute micro-recovery breaks, psychological offline boundaries, Swiss-cheese action launch, 3-sentence upward alignment |
| 🎓 **Campus & Higher-Ed** | Academic overwhelm, thesis procrastination, exam & defense nervousness, job hunting stress | 15-minute start commands, cognitive overload reduction, campus counseling referral pathway |
| 🔒 **Compliance & Safety** | Severe crisis signals, self-harm expressions, acute helplessness | Millisecond rule interception, blocking model generation and outputting emergency hotline referrals |

---

## 💻 Quick Links

- `Commercial Whitepaper`:[docs/commercialization.md](docs/commercialization.md)
- `Docker Production Guide`:[docs/deployment-docker.md](docs/deployment-docker.md)
- `Try online (Static Demo)`:[Live Demo](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
- `Download package`:[Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)
- `Chinese documentation`:[README.md](README.md)
- `Model setup`:[docs/model-integration.en.md](docs/model-integration.en.md)
- `API reference`:[docs/api-reference.en.md](docs/api-reference.en.md)
- `Troubleshooting`:[docs/troubleshooting.en.md](docs/troubleshooting.en.md)

---

## 🛠️ Production Deployment

### Option 1: Docker Compose Full Stack (Recommended)

```bash
# 1. Copy production environment file
cp .env.production .env

# 2. Build and launch API container + Nginx reverse proxy
docker compose up -d --build
```

Access endpoints:
- **Web Console**: `http://localhost` (Nginx port 80, SSE buffering disabled)
- **API Swagger Documentation**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost/metrics`

### Option 2: Kubernetes Cluster

Apply production manifests from [deploy/k8s/deployment.yaml](deploy/k8s/deployment.yaml):
```bash
kubectl apply -f deploy/k8s/deployment.yaml
```

### Option 3: Local Friction-free Windows Startup

For rapid developer evaluation on Windows:
```powershell
.\start-web.ps1
```
Or run preflight diagnostics:
```powershell
.\doctor.ps1
```

Run test suite (57+ unit and integration tests):
```powershell
pytest -vv
```

---

## 🔌 API Overview

- `POST /chat/stream`: **[NEW]** Server-Sent Events (SSE) real-time typewriter chat stream
- `GET /metrics`: **[NEW]** Standard Prometheus metrics scraping endpoint
- `GET /api/scenarios`: **[NEW]** Business scenarios catalog (Campus vs Enterprise EAP)
- `GET /api/sessions`: **[NEW]** Paginated session history summaries
- `DELETE /api/sessions/{id}`: **[NEW]** Clear conversation session
- `DELETE /api/knowledge/documents/{id}`: **[NEW]** Delete custom knowledge document
- `POST /chat`: Classic synchronous chat completion
- `GET /health`: System health check with probe metadata
- `GET /api/meta`: Service runtime metadata and model configurations
- `GET /api/compatibility`: Provider compatibility and key preflight report
- `GET /api/knowledge/search`: RAG excerpt retrieval
- `POST /api/knowledge/documents`: Add custom Markdown policy/SOP
- `POST /api/feedback`: Turn rating and quality feedback

---

## 📄 License

This repository is distributed under the [MIT License](LICENSE).
For commercial private deployments and custom EAP modules, see [docs/commercialization.md](docs/commercialization.md).
