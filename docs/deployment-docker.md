# 知愈星 AI (ZhiYuXing Copilot) 工业级容器化与生产部署指南

本指南面向运维工程师与系统管理员，介绍如何在 Linux/macOS/Windows 环境下进行知愈星 AI 的生产级部署、Nginx 反向代理配置、SSE 流式传输优化以及监控对接。

---

## 1. 架构总览

生产环境标准拓扑如下：

```text
[ 客户端浏览器 / 移动端 / 企微/钉钉 ]
                 │
                 ▼ (HTTPS :443 / HTTP :80)
   ┌───────────────────────────┐
   │    Nginx 反向代理网关       │  <- Gzip 压缩, 安全响应头, 限流
   │ (proxy_buffering off: SSE)│  <- 静态资源缓存, SSL 终止
   └─────────────┬─────────────┘
                 │
                 ▼ (HTTP :8000)
   ┌───────────────────────────┐
   │  ZhiYuXing API 后端容器    │  <- FastAPI + Uvicorn (多 Worker)
   │  (Python 3.13-slim, 非root)│  <- Prometheus /metrics, 链路追踪
   └─────────────┬─────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
[ 数据卷持久化 SQLite ]    [ 企业知识库上传卷 ]
```

---

## 2. 方式一：Docker Compose 一键部署 (推荐)

仓库已内置生产就绪的编排配置 `docker-compose.yml` 与 `docker-compose.prod.yml`。

### 步骤 1：准备配置文件
```bash
# 复制生产级环境配置模板
cp .env.production .env

# 根据需要编辑配置（填入 API Key，或保持默认免 Key 本地演示模式）
vim .env
```

### 步骤 2：启动服务栈
```bash
# 构建并启动 API 服务容器与 Nginx 反向代理
docker compose up -d --build

# 或者使用生产配置启动
docker compose -f docker-compose.prod.yml up -d
```

### 步骤 3：验证运行状态
```bash
# 检查容器运行状态与健康探针
docker compose ps

# 查看实时日志
docker compose logs -f api
```

访问入口：
- **Web 控制台**：`http://localhost` (通过 Nginx 80 端口)
- **直接后端接口**：`http://localhost:8000`
- **Prometheus 指标**：`http://localhost/metrics`
- **Swagger API 文档**：`http://localhost/docs`

---

## 3. 关键生产调优说明

### 3.1 SSE 实时流式输出 (Server-Sent Events) 调优
对于大模型的打字机流式输出，Nginx 必须关闭代理缓冲 (`proxy_buffering off;`)，否则客户端必须等整个回复生成完毕后才能一次性收到数据：

```nginx
location /chat/stream {
    proxy_pass http://zhiyuxing_backend/chat/stream;
    proxy_http_version 1.1;
    proxy_set_header Connection "";

    # 关键设置：关闭缓冲以支持即时推流
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
    proxy_read_timeout 300s;
}
```

### 3.2 启用企业级 API Key 鉴权保护
在生产模式下，若需防止未授权调用，可以在 `.env` 中开启鉴权：

```env
API_KEY_AUTH_ENABLED=true
API_MASTER_KEYS=your-enterprise-secret-key-1,your-enterprise-secret-key-2
```
开启后，所有访问 `/chat` 和 `/chat/stream` 的请求必须携带 Header：
- `X-API-Key: your-enterprise-secret-key-1` 或
- `Authorization: Bearer your-enterprise-secret-key-1`

### 3.3 Prometheus + Grafana 可观测性接入
服务内置了兼容 Prometheus 的标准指标输出接口：`GET /metrics`。
指标涵盖：
- `zhiyuxing_uptime_seconds`：服务已运行时长。
- `zhiyuxing_http_requests_total`：HTTP 请求总数（按方法、路径与状态码）。
- `zhiyuxing_chat_requests_total`：AI 对话总数（按模式、提供商、模型与场景区分）。
- `zhiyuxing_safety_guardrail_triggers_total`：安全围栏拦截次数。
- `zhiyuxing_tokens_estimated_total`：Token 估算消耗。

在 `prometheus.yml` 中添加抓取任务即可：
```yaml
scrape_configs:
  - job_name: 'zhiyuxing_copilot'
    scrape_interval: 15s
    static_configs:
      - targets: ['api:8000']
```

---

## 4. 方式二：Kubernetes 集群部署

若需在企业私有云或公有云 K8s 集群中部署，直接应用 `deploy/k8s/deployment.yaml`：

```bash
kubectl apply -f deploy/k8s/deployment.yaml
```

该清单已内置：
- 2 副本的高可用 Deployment
- 存活探针 (Liveness) 与就绪探针 (Readiness)
- PVC 数据卷挂载
- Ingress 路由及 SSE 关闭缓冲注解 (`nginx.ingress.kubernetes.io/proxy-buffering: "off"`)

---

## 5. 故障排查与日志排查

| 现象 | 可能原因 | 解决方式 |
|---|---|---|
| 页面流式输出卡顿，一次性吐出整段话 | Nginx 开启了响应缓冲 | 确保 Nginx 中 `proxy_buffering off;` 生效 |
| 容器重启或健康检查失败 | 端口冲突或未就绪 | 执行 `curl -f http://127.0.0.1:8000/health` 查看返回详情 |
| 数据在容器重启后丢失 | 未挂载宿主机持久化卷 | 检查 `docker-compose.yml` 中的 `./data:/app/data` 挂载路径 |
