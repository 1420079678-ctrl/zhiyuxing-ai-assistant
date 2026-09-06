from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import router
from backend.config import DOCS_DIR, STATIC_DIR, cors_origins
from services.storage import ensure_database
from services.telemetry import telemetry


APP_TITLE = "Zhiyuxing AI Copilot Enterprise API"
APP_DESCRIPTION = "知愈星 AI (ZhiYuXing Copilot) · 企业级多场景心身关怀与行动赋能智能体平台，支持高校与企业 EAP 双场景。"
APP_VERSION = "1.0.0"


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

    # 1. Enable CORS for multi-domain SaaS integration
    origins = cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Request Tracing & Telemetry Middleware
    @app.middleware("http")
    async def trace_and_telemetry_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
            telemetry.record_request(request.method, request.url.path, response.status_code, duration)
            return response
        except Exception as exc:
            duration = time.time() - start_time
            telemetry.record_request(request.method, request.url.path, 500, duration)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "request_id": request_id,
                    "detail": f"Internal Server Error: {exc}",
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Response-Time": f"{duration * 1000:.2f}ms",
                },
            )

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/project-docs", StaticFiles(directory=DOCS_DIR), name="project-docs")
    app.include_router(router)
    return app


app = create_app()
