# Release 压缩包安装说明

如果使用者不想装 Git，也不想自己执行一堆命令，最推荐的方式就是直接下载 GitHub Releases 里的压缩包。

## 下载方式

打开 Releases 页面：

- [Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)

下载资产中的：

- `zhiyuxing-ai-assistant-release-v*.zip`

不要下载：

- GitHub 自动生成的 `Source code (zip)`
- GitHub 自动生成的 `Source code (tar.gz)`

原因：

- 自动生成的源码包没有额外整理过的安装入口
- Release 压缩包里会附带启动脚本、诊断脚本和安装提示

## Windows 用户安装步骤

### 1. 安装 Python 3.13

需要先装 Python，且安装时建议勾选加入 PATH。

### 2. 解压 Release 压缩包

例如解压到：

```text
C:\Users\你的用户名\Desktop\zhiyuxing-ai-assistant
```

### 3. 双击启动

直接运行：

```text
start-web.bat
```

首次启动会自动：

- 创建 `.venv`
- 安装依赖
- 复制 `.env`
- 启动本地 Web 服务

### 4. 打开页面

浏览器访问：

- `http://127.0.0.1:8000/`

## 如果启动失败

先运行：

```text
doctor.bat
```

或者：

```powershell
.\doctor.ps1
```

它会自动判断：

- 是否不在项目目录
- Python 是否安装
- `.venv` 是否可创建
- 依赖是否安装完整
- 端口 `8000` 是否被占用

## 真实模型调用说明

Release 压缩包默认也可以直接跑，但默认是 demo mode。

如果要接真实模型，再按这些文档配置：

- [docs/model-integration.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/model-integration.md)
- [docs/troubleshooting.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/troubleshooting.md)

## 维护者如何生成新的 Release 压缩包

在仓库根目录运行：

```powershell
.\build-release.ps1 -Version v0.7.0
```

或：

```text
build-release.bat v0.7.0
```

生成结果默认放在：

```text
dist\
```
