# 知愈星 AI Assistant (ZhiYuXing Copilot)

[中文](README.md) | [English](README_EN.md)

在线体验（GitHub Pages 纯静态演示）：`https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/`

![Version 1.0.0](https://img.shields.io/badge/Release-v1.0.0--Enterprise-blue.svg)
![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Service-009688?logo=fastapi&logoColor=white)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus&logoColor=white)
![CI](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Stars](https://img.shields.io/github/stars/1420079678-ctrl/zhiyuxing-ai-assistant?style=social)](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant)

**知愈星 AI (ZhiYuXing Copilot)** 是一个企业级多场景心身关怀与行动赋能智能体平台。区别于泛化闲聊或静态问答，本项目立足严肃的心理支持与组织效能场景，聚焦高频的 **【企业员工 EAP 职场关怀】** 与 **【高校青年学业成长】** 双场景，输出温和共情、深度 RAG 知识检索、合规级风险阻断与高执行力的微步行动建议。

项目具备 **工业级容器化成熟部署方案**（Docker、Docker Compose、Nginx 生产反代、Kubernetes 编排），支持 **SSE 实时流式响应 (`POST /chat/stream`)** 与 **Prometheus 可观测性监控 (`GET /metrics`)**，兼顾商业私有化落地与开箱即用的本地演示。

如果这个项目对你有帮助，欢迎点一个 `Star` ⭐。

---

## 🌟 OrcaRouter 推荐模型路由网关

[![OrcaRouter 推荐网关](https://img.shields.io/badge/OrcaRouter-Recommended_Gateway-2563eb)](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f)

在高并发生产与多模型调度场景中，可通过项目已有的 OpenAI 兼容配置接入 OrcaRouter，在自托管后端中统一调度各家大模型服务。详见 [OrcaRouter 接入指南](docs/orcarouter.md)，包含可重放配置命令、密钥设置、验证和回滚步骤。

- [前往 OrcaRouter 官网](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f) · [官方快速开始](https://docs.orcarouter.ai/getting-started/quickstart)
- 上述链接为项目推荐链接；通过该链接使用服务，维护者可能获得推荐收益。
- 状态记录（2026-09-06）：推广计划已生效；开源目录尚未发布，应用标识尚未签发。本文提供配置接入方式，尚未完成真实 API 调用验证，不代表官方背书。
- GitHub Pages 演示仍使用本地演示逻辑；真实调用需自行配置后端和 API Key。

---

## 🚀 核心商业场景

| 业务场景 | 覆盖痛点与场景需求 | 赋能机制与核心输出 |
|---|---|---|
| 🏢 **企业员工 EAP 关怀** | 高强度交付疲惫、职业倦怠 (Burnout)、无意义感、跨部门沟通对齐摩擦 | 工位 5分钟微能量回血、心理离线边界建立、瑞士奶酪式行动破冰、向上对齐三句法 |
| 🎓 **高校青年成长** | 学业压力堆积、论文拖延内耗、考试与毕业答辩紧张、求职迷茫 | 15分钟微步启动指令、认知负荷卸载、高校心理中心线下转介机制 |
| 🔒 **合规风险围栏** | 重度抑郁表达、危机言语、自我否定与高危倾向 | 毫秒级规则匹配、强阻断并输出固定危机干预热线与转介建议 |

---

## 💻 快速导航

- `商业落地白皮书`：[docs/commercialization.md](docs/commercialization.md)
- `生产级 Docker 部署`：[docs/deployment-docker.md](docs/deployment-docker.md)
- `在线体验 (静态演示)`：[Live Demo](https://1420079678-ctrl.github.io/zhiyuxing-ai-assistant/)
- `下载发布包`：[Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)
- `英文说明`：[README_EN.md](README_EN.md)
- `模型接入指南`：[docs/model-integration.md](docs/model-integration.md)
- `API 接口参考`：[docs/api-reference.md](docs/api-reference.md)
- `钉钉场景集成`：[docs/dingtalk-integration.md](docs/dingtalk-integration.md)
- `启动排障手册`：[docs/troubleshooting.md](docs/troubleshooting.md)

---

## 🛠️ 工业级生产部署

### 方式一：Docker Compose 全栈一键部署 (推荐)

仓库已内置生产级多阶段构建 `Dockerfile`、`docker-compose.yml` 与带安全调优的 `deploy/nginx/nginx.conf`：

```bash
# 1. 复制生产环境变量文件
cp .env.production .env

# 2. 一键拉起完整服务栈 (API + Nginx 反代 + 存储卷挂载)
docker compose up -d --build
```

启动后即可访问：
- **Web 控制台**：`http://localhost` (Nginx 80 端口，反向代理并禁用 SSE 缓冲)
- **后端 Swagger 文档**：`http://localhost:8000/docs`
- **Prometheus 监控端点**：`http://localhost/metrics`

### 方式二：Kubernetes 集群生产编排

企业级 K8s 部署清单位于 [deploy/k8s/deployment.yaml](deploy/k8s/deployment.yaml)，直接应用即可：
```bash
kubectl apply -f deploy/k8s/deployment.yaml
```

### 方式三：Windows 一键快速启动 (开发者本地免配置)

如果你在 Windows 本地开发，可以直接运行仓库根目录自带脚本，自动创建虚拟环境并补全依赖：

```powershell
.\start-web.ps1
```
或直接双击 `start-web.bat`。

启动前可通过诊断脚本检查环境健康度：
```powershell
.\doctor.ps1
```

运行完整自动化回归测试（57+ 用例全覆盖）：
```powershell
pytest -vv
```

---

## 📐 系统工程结构

```text
backend/
  api/            # API 路由层 (REST、SSE 流式、Prometheus 监控)
  app_factory.py  # FastAPI 应用装配、Request-ID 链路追踪中间件、CORS
  chat_logic.py   # 高校与企业双场景提示词、风格引擎与 Demo 逻辑
  chat_service.py # 完整对话流与 SSE 异步流式生成器
  config.py       # 运行配置、模型网关预设、场景定义
  runtime.py      # 模型解析与兼容性检查
  schemas.py      # Pydantic 数据契约
services/
  auth.py         # 企业级 API Key 鉴权与租户保护
  knowledge.py    # RAG 知识检索与动态文档增删
  safety.py       # 风险识别与合规安全围栏
  storage.py      # SQLite 优化 WAL 模式与多会话持久化
  telemetry.py    # Prometheus 兼容遥测采集器 (QPS/延迟/Token)
deploy/
  nginx/          # Nginx 生产反向代理与 SSE 流式配置
  k8s/            # Kubernetes 生产编排清单
  scripts/        # 自动化部署运维脚本
knowledge_base/   # 高校心理支持与企业 EAP 核心知识库
static/           # SaaS 级 Copilot 控制台前端
tests/            # 自动化测试套件 (API、Services、Streaming、Scenarios)
```

---

## 🔌 核心接口一览

- `POST /chat/stream`：**[新增]** Server-Sent Events (SSE) 实时打字机流式对话
- `GET /metrics`：**[新增]** Prometheus 标准监控数据抓取接口
- `GET /api/scenarios`：**[新增]** 业务场景模式列表 (Campus vs Enterprise EAP)
- `GET /api/sessions`：**[新增]** 会话历史列表与分页摘要
- `DELETE /api/sessions/{session_id}`：**[新增]** 清除指定会话记录
- `DELETE /api/knowledge/documents/{doc_id}`：**[新增]** 删除自定义知识文档
- `POST /chat`：经典阻塞式对话接口
- `GET /health`：服务健康检查 (带探针元信息)
- `GET /api/meta`：运行环境元信息与多模型状态
- `GET /api/compatibility`：模型接入合规与连接预检
- `GET /api/knowledge/search`：RAG 知识片段切片检索
- `POST /api/knowledge/documents`：上传自定义 Markdown/SOP 政策
- `POST /api/feedback`：回复满意度与质量反馈

---

## 🛡️ 安全合规与免责声明

1. **定位明确**：知愈星 AI 定位为心身关怀与行动赋能辅助工具，严禁用于精神科医学临床诊断、药物处方或替代专业医疗。
2. **危机干预兜底**：系统对自伤、伤人、持续严重精神耗竭等风险表达实施强拦截，优先输出官方心理援助热线与线下就医指引。
3. **数据安全**：自托管与私有化部署模式下，数据完全隔离于本地或企业私有 VPC，不回流公网模型服务商。

---

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 许可证开源，保留既往所有版本演进记录。
商业化解决方案与专有私有化部署服务请参阅 [docs/commercialization.md](docs/commercialization.md)。
