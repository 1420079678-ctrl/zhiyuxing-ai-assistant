# Release Package Installation

If a user does not want to install Git or run several setup commands manually, the best option is to download the packaged zip from GitHub Releases.

## Where to download

Open the Releases page:

- [Latest Release](https://github.com/1420079678-ctrl/zhiyuxing-ai-assistant/releases/latest)

Download the asset named like:

- `zhiyuxing-ai-assistant-release-v*.zip`

Do not use:

- GitHub-generated `Source code (zip)`
- GitHub-generated `Source code (tar.gz)`

Why:

- GitHub source archives are raw source snapshots
- the release package includes launcher scripts, diagnostics, and install guidance

## Windows setup steps

### 1. Install Python 3.13

Python must be installed first. Enable the PATH option during installation.

### 2. Extract the release zip

For example:

```text
C:\Users\YourName\Desktop\zhiyuxing-ai-assistant
```

### 3. Start the app

Double-click:

```text
start-web.bat
```

On first launch it will automatically:

- create `.venv`
- install dependencies
- copy `.env`
- start the local web service

### 4. Open the page

Visit:

- `http://127.0.0.1:8000/`

## If startup fails

Run:

```text
doctor.bat
```

or:

```powershell
.\doctor.ps1
```

This checks:

- whether the folder is correct
- whether Python is installed
- whether `.venv` can be created
- whether dependencies were installed
- whether port `8000` is already used

## Real model calls

The release package can run immediately, but defaults to demo mode.

If real model calls are needed, follow:

- [docs/model-integration.en.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/model-integration.en.md)
- [docs/troubleshooting.en.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/troubleshooting.en.md)

## Maintainer command to build a new release package

From the repository root:

```powershell
.\build-release.ps1 -Version v0.7.0
```

or:

```text
build-release.bat v0.7.0
```

Artifacts are created in:

```text
dist\
```
