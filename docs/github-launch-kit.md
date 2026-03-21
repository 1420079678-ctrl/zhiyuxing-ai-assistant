# GitHub 发布与传播清单

这份文档不是项目功能文档，而是仓库运营清单，方便把项目更完整地展示在 GitHub 上，并用于后续发布和传播。

## 1. 仓库 About 建议

### Description

```text
AI emotional support and study assistant for students, with FastAPI web UI, local demo mode, and OpenAI/DeepSeek-compatible integration.
```

### Topics

```text
fastapi, python, ai-assistant, chatbot, openai-compatible, deepseek, mental-health, student-support, study-assistant, webapp, dingtalk
```

### Website

```text
https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/
```

## 2. Social Preview

推荐直接使用仓库内现成图片：

- `docs/assets/12-social-preview.png`

如果后续项目定位有变化，可以重新运行：

```powershell
.\.venv\Scripts\python scripts\generate_social_preview.py
```

## 3. Release 建议

当前已经打好标签：

- `v0.1.0`

推荐在 GitHub 上创建 release：

### Title

```text
v0.1.0 · First public runnable release
```

### Release Notes

```md
First public runnable release of Zhiyuxing AI Assistant.

Highlights:
- Standalone FastAPI web app with browser UI
- Local demo mode that works without API keys
- One-click provider presets for OpenAI, DeepSeek Chat, and DeepSeek R1
- Compatibility preflight checks and optional live probe
- Bilingual GitHub documentation in Chinese and English

This release is intended to make the project easier to run, understand, and extend.
```

## 4. 个人主页展示建议

- 把该仓库 pin 到 GitHub 个人主页
- 如果你有 Profile README，可以把这个项目作为代表项目单独展示
- 不要一次 pin 太多项目，优先保证这个项目在第一屏可见

## 5. 中文发布文案模板

```text
做了一个面向大学生场景的 AI 情绪支持与学习辅助项目：知愈星 AI Assistant。

这个项目不是只放方案文档，而是已经整理成了可以直接运行的 FastAPI + Web 项目：
- 支持本地 demo 模式，没填 API Key 也能跑
- 支持一键切 OpenAI / DeepSeek Chat / DeepSeek R1
- 支持 API 兼容性检查和最小真实探测
- GitHub 文档中英双语

比较适合用来展示：
1. 一个有明确场景的 AI 应用
2. 一个可运行、可继续扩展的完整项目
3. Web 端与平台接入边界清晰的工程化仓库

项目地址：
https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant

如果你觉得这个方向有参考价值，欢迎 Star。
```

## 6. 英文发布文案模板

```text
I turned Zhiyuxing AI Assistant into a runnable open-source project.

It is an AI emotional support and study assistance service for student scenarios, built with FastAPI and a web UI.

Current highlights:
- local demo mode that works without API keys
- one-click provider setup for OpenAI, DeepSeek Chat, and DeepSeek R1
- compatibility preflight checks and optional live probe
- bilingual GitHub documentation

Repo:
https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant

If it is useful, a star would mean a lot.
```

## 7. 发布顺序建议

1. 先完善 GitHub About、topics 和 social preview
2. 创建 `v0.1.0` release
3. 再去外部平台发帖引流
4. 外部内容统一指向 GitHub 仓库首页
