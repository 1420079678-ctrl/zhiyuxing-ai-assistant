# API Reference

This document complements Swagger by showing the practical capability surface of the project.

## API Groups

### Runtime and Status

- `GET /health`
- `GET /api/meta`
- `GET /api/compatibility`

### Chat and Feedback

- `POST /chat`
- `GET /api/session/{session_id}`
- `POST /api/feedback`

### Knowledge Base

- `GET /api/knowledge/search?q=keyword`
- `GET /api/knowledge/documents`
- `POST /api/knowledge/documents`

## Key Endpoints

### `POST /chat`

Runs a complete response pipeline with:

- model selection
- session memory
- local knowledge retrieval
- risk detection
- SQLite persistence

Example request:

```json
{
  "message": "I feel intense exam stress and I have started losing sleep.",
  "response_style": "structured",
  "model_target": "configured",
  "session_id": null
}
```

### `GET /api/session/{session_id}`

Returns recent session history so the frontend can restore previous turns and continue multi-turn conversations.

### `POST /api/knowledge/documents`

Writes a new document into the custom local knowledge base. Once written, it becomes searchable immediately.

Example request:

```json
{
  "title": "Campus Support Channels",
  "content": "If a user reports ongoing insomnia, overwhelm, or severe low mood, the assistant should explicitly suggest the school counseling center, counselor, or campus clinic."
}
```

## Current Scope

- The public GitHub Pages page is mainly a static preview and does not include backend write capabilities.
- Knowledge document creation, session history, and feedback persistence are available when the FastAPI backend is running locally.
- The current retrieval layer is a lightweight local RAG-style implementation, suitable for demos and extensible prototypes rather than a heavy vector database stack.
