from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import router
from backend.config import DOCS_DIR, STATIC_DIR
from services.storage import ensure_database


APP_TITLE = "Zhiyuxing AI Assistant API"
APP_DESCRIPTION = "面向大学生场景的 AI 情绪支持与学习辅助服务，支持本地演示模式与模型调用模式。"
APP_VERSION = "0.7.0"


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/project-docs", StaticFiles(directory=DOCS_DIR), name="project-docs")
    app.include_router(router)
    return app


app = create_app()
