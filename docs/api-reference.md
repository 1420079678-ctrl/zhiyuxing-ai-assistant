# API 参考

这份文档用于补充 Swagger 之外的接口理解，方便快速看清这个项目现在已经具备哪些“可用能力”。

## 接口分组

### 运行与状态

- `GET /health`
- `GET /api/meta`
- `GET /api/compatibility`

### 对话与反馈

- `POST /chat`
- `GET /api/session/{session_id}`
- `POST /api/feedback`

### 知识库

- `GET /api/knowledge/search?q=关键词`
- `GET /api/knowledge/documents`
- `POST /api/knowledge/documents`

## 关键接口

### `POST /chat`

用于发起一轮完整对话。系统会自动串联：

- 模型选择
- 会话记忆
- 本地知识检索
- 风险识别
- SQLite 持久化

请求示例：

```json
{
  "message": "最近考试压力很大，晚上总失眠。",
  "response_style": "structured",
  "model_target": "configured",
  "session_id": null
}
```

### `GET /api/session/{session_id}`

返回最近会话历史，用于：

- 前端恢复对话
- 检查本地持久化是否生效
- 继续多轮提问

### `POST /api/knowledge/documents`

向自定义知识库写入一份文档。写入后，新文档会立即参与后续检索和回复增强。

请求示例：

```json
{
  "title": "校园心理支持渠道",
  "content": "如果用户连续失眠、明显崩溃或长期低落，应明确建议联系学校心理中心、辅导员或校医院。"
}
```

返回示例：

```json
{
  "status": "ok",
  "message": "知识文档已写入自定义知识库，可立即参与后续检索和回答。",
  "document": {
    "document_id": "xiao-yuan-xin-li-zhi-chi-qu-dao",
    "title": "校园心理支持渠道",
    "source_path": "data/knowledge_uploads/xiao-yuan-xin-li-zhi-chi-qu-dao.md",
    "category": "custom"
  }
}
```

## 当前能力边界

- GitHub Pages 公开页主要用于静态演示，不包含后端写入能力。
- 本地启动 FastAPI 服务后，才可以使用知识文档写入、会话历史和反馈记录。
- 当前知识检索是轻量化本地 RAG 方案，适合 Demo、课程项目和可扩展原型，不是重型向量数据库方案。
