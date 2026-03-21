# Troubleshooting

If someone fails to start the project on their first try, do not ask them to manually fix the environment first. Use these two commands:

```powershell
cd zhiyuxing-ai-assistant
.\doctor.ps1
```

Then start the app:

```powershell
.\start-web.ps1
```

## What `doctor.ps1` checks

- whether the current directory is the repository root
- whether a usable Python launcher exists
- whether `.venv` can be created automatically
- whether dependencies are installed
- whether `.env` exists
- whether port `8000` is already occupied
- whether the current model configuration is ready for real API calls

## Most common failure cases

### 1. Running commands outside the project folder

Wrong example:

```powershell
C:\Users\xxx> python -m pytest -vv
```

That uses the system Python and is usually not inside the repository root.

Correct:

```powershell
cd zhiyuxing-ai-assistant
.\run-tests.ps1
```

### 2. Python is not installed

Symptoms:

- `py` or `python` does not exist
- `doctor.ps1` reports `No usable Python launcher found`

Fix:

- install Python 3.13
- enable the PATH option during installation

### 3. Port 8000 is already in use

Symptoms:

- `start-web.ps1` reports that the address is already in use

Fix:

- stop the process currently using port `8000`
- or start `uvicorn` on a different port manually

### 4. Real model calls are not configured

Symptoms:

- compatibility checks show a warning
- the project still starts successfully

Fix:

- without an API key, the app falls back to demo mode
- if real model calls are needed, configure them through [docs/model-integration.en.md](/Users/X1973/Documents/Playground/zhiyuxing-ai-assistant/docs/model-integration.en.md)

## Best instructions to send other people

Use these first:

```powershell
cd zhiyuxing-ai-assistant
.\start-web.ps1
```

If it fails, send this next:

```powershell
.\doctor.ps1
```
