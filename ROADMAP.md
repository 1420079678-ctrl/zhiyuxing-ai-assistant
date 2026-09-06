# Roadmap (知愈星 AI 演进路线图)

## Completed in v1.0.0 (Commercial & Enterprise Transformation)
- [x] 工业级容器化成熟部署方案 (Multi-stage Docker, Docker Compose, Nginx 反代配置, Kubernetes 清单)
- [x] Server-Sent Events (SSE) 实时打字机流式输出 (`POST /chat/stream`)
- [x] Prometheus 生产级监控指标采集端点 (`GET /metrics`) 与链路追踪中间件 (`X-Request-ID`, `X-Response-Time`)
- [x] 拓展企业员工 EAP 关怀场景 (职业倦怠修复、精力管理、微行动破冰、向上管理对齐)
- [x] 现代化 SaaS 级 Copilot 控制台 UI (多会话抽屉、流式消息气泡、RAG 切片穿透检视器)
- [x] 知识库动态管理 API 与文件增删支持 (`DELETE /api/knowledge/documents/{id}`)
- [x] 企业级 API Key 鉴权与租户保护模块 (`services/auth.py`)

## Next Milestones (v1.1.0 - v1.2.0)
- [ ] 向量数据库检索增强 (基于 pgvector / Qdrant 的密集语义向量检索混合召回)
- [ ] 飞书、钉钉、企业微信机器人企业应用一键 Webhook/OAuth 深度互联插件
- [ ] 多组织多租户数据沙箱与独立知识库隔离
- [ ] 心理咨询师/企业HR管理端后台 (咨询预约转介看板、危机预警工单通知推送)
- [ ] 语音输入与轻量语音回复合成 (TTS) 关怀通道

## Long Term Vision
- 打造开箱即用、安全合规的企业级组织心身关怀与人机协同赋能标准基础设施。
