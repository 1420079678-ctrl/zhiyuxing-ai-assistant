# 受限公开后端体验

这个项目现在支持一个“真正可访问，但受限”的后端演示模式。

## 它是什么

通过本地 FastAPI 服务加临时公网隧道，把你的本机后端暴露为一个可直接访问的 URL。

适合：

- 给老师、同学、面试官临时体验真实后端
- 展示 `/chat`、`/docs`、`/api/meta` 等接口
- 演示“这不是纯静态页面，而是有真实 API 的项目”

## 它的限制

这个模式会自动启用：

- `DEMO_MODE=true`
- `PUBLIC_DEMO_MODE=true`

因此它具备以下限制：

- 固定运行在本地 demo 模式，不会发起真实模型调用
- 禁止写入 `/api/knowledge/documents`
- 禁止写入 `/api/feedback`
- 公网链接只在你的机器和脚本持续运行时有效

## 启动方式

```powershell
.\start-public-demo.ps1
```

或双击：

```text
start-public-demo.bat
```

脚本会：

1. 启动一个专用本地后端
2. 自动通过 `localhost.run` 建立临时公网隧道
3. 输出一个可直接访问的临时 URL

通常会得到类似 `https://xxxxx.lhr.life` 或 `https://xxxxx.localhost.run` 的地址。

拿到地址后，最值得直接验证的是：

- `GET /health`
- `GET /api/meta`
- `POST /chat`
- `GET /docs`

## 最适合怎么用

最推荐的对外说明方式是：

- `公开静态演示`：GitHub Pages
- `公开受限后端演示`：临时公网隧道
- `完整本地 / 真实模型版`：开发者本机运行

这个方案的定位不是正式生产部署，而是“让别人真的能访问到后端”的轻量演示方式。
