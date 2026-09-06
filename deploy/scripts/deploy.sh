#!/usr/bin/env bash
set -euo pipefail

# Enterprise deployment helper script for ZhiYuXing AI Assistant
echo "======================================================="
echo " ZhiYuXing AI Copilot - Enterprise Production Deployment "
echo "======================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT_DIR}"

# 1. Check environment file
if [ ! -f .env ] && [ ! -f .env.production ]; then
    echo "[!] No .env or .env.production found. Creating default .env from .env.example..."
    cp .env.example .env
fi

# 2. Pull or build container images
echo "[+] Building production Docker image..."
docker compose -f docker-compose.prod.yml build

# 3. Start services with rolling checks
echo "[+] Launching containers..."
docker compose -f docker-compose.prod.yml up -d

# 4. Wait for health check
echo "[+] Verifying service health..."
TIMEOUT=40
while [ $TIMEOUT -gt 0 ]; do
    if curl -s -f http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "[✓] ZhiYuXing Copilot service is healthy and online!"
        break
    fi
    sleep 2
    TIMEOUT=$((TIMEOUT - 2))
done

if [ $TIMEOUT -le 0 ]; then
    echo "[✗] Service healthcheck timed out. Review logs with: docker compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo "======================================================="
echo " Deployment successful!"
echo " Web Console: http://127.0.0.1"
echo " API Docs:    http://127.0.0.1/docs"
echo " Metrics:     http://127.0.0.1/metrics"
echo "======================================================="
