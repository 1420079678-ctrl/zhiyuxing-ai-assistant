.PHONY: help install dev test lint docker-build docker-up docker-down clean

help:
	@echo "知愈星 AI (ZhiYuXing Copilot) 运维指令集"
	@echo "--------------------------------------------------"
	@echo "  make install       安装生产与开发依赖"
	@echo "  make dev           启动本地热重载开发服务"
	@echo "  make test          执行全量自动化测试"
	@echo "  make docker-build  构建生产 Docker 镜像"
	@echo "  make docker-up     启动 Docker Compose 服务栈 (API + Nginx)"
	@echo "  make docker-down   停止 Docker Compose 服务栈"
	@echo "  make clean         清理缓存与临时文件"

install:
	pip install -e ".[dev]"

dev:
	python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

test:
	pytest -vv

docker-build:
	docker build -t zhiyuxing-ai-assistant:latest .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
