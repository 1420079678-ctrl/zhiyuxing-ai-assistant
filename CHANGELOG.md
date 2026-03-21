# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

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
