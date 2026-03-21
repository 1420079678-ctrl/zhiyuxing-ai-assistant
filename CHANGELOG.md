# Changelog

All notable changes to this project are documented in this file.

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

## [Unreleased]

### Added

- local markdown knowledge base and retrieval endpoint
- SQLite-backed session persistence and session history endpoint
- feedback recording endpoint for recent assistant replies
- rule-based risk detection with high-risk guardrail fallback

### Improved

- web UI now shows session id, memory usage, risk level, knowledge hits, and recent history
- README and usage guides now distinguish public preview mode from full local backend capabilities
- test coverage now verifies knowledge retrieval, memory flow, high-risk handling, and feedback persistence
