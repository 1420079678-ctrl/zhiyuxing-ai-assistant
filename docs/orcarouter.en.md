# OrcaRouter Integration

[中文](orcarouter.md) | [English](orcarouter.en.md)

OrcaRouter is an optional OpenAI-compatible provider for this project. The existing backend selects it through the base URL, model name, and key environment variable; the chat API does not need to change.

## 1. Account and API key

Sign in through the [project referral link](https://www.orcarouter.ai/ref/ref_f60521be8c405c4c116f) or the [OrcaRouter website](https://www.orcarouter.ai/), then create your own API key in the console. The maintainer may receive referral revenue. Availability and charges depend on your account and the service's current terms.

Use `https://api.orcarouter.ai/v1` as the base URL. The example model `openai/gpt-4o-mini` comes from the official quickstart; choose an available model ID from your account or `/v1/models`.

## 2. Configure the self-hosted backend

Install the project dependencies and create `.venv` as described in the [README](../README_EN.md). Run the following from the project root to back up `.env` and reuse the existing configuration script:

```powershell
# Run from the project root after installing the project dependencies.
if (Test-Path -LiteralPath .env) {
  if (Test-Path -LiteralPath .env.before-orcarouter) {
    throw "Existing .env.before-orcarouter backup found; keep it safe before repeating this step."
  }
  Copy-Item -LiteralPath .env -Destination .env.before-orcarouter
}
.\.venv\Scripts\python scripts\setup_model_config.py `
  --preset openai `
  --provider-name OrcaRouter `
  --base-url https://api.orcarouter.ai/v1 `
  --model-name openai/gpt-4o-mini `
  --api-key-env ORCAROUTER_API_KEY `
  --demo-mode false
```

The `openai` preset is only a starting template. The overrides select OrcaRouter's URL, display name, model, and separate key variable; they do not send the OrcaRouter key to OpenAI's official endpoint.

On the first interactive run, the script asks for `ORCAROUTER_API_KEY` using visible terminal input. You can leave it blank and edit that variable in your local `.env` afterward. Keep real keys out of shell commands, documentation, screenshots, and GitHub.

Verify these local values, with only one effective definition per variable:

```dotenv
OPENAI_BASE_URL=https://api.orcarouter.ai/v1
MODEL_NAME=openai/gpt-4o-mini
MODEL_PROVIDER=OrcaRouter
MODEL_API_KEY_ENV=ORCAROUTER_API_KEY
ORCAROUTER_API_KEY=
DEMO_MODE=false
PUBLIC_DEMO_MODE=false
```

Fill the empty key locally. Also verify `PUBLIC_DEMO_MODE=false`: the setup script preserves its previous value. Existing process environment variables can take precedence over `.env`.

Restart the backend and select the current configured target for OrcaRouter in the web model selector. The separate OpenAI and DeepSeek presets still select their own official endpoints. These instructions do not add a dedicated OrcaRouter dropdown preset.

## 3. Verify configuration and a live request

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

Check the provider, base URL, model name, and key variable. The current checker warns about custom compatible endpoints; a configuration check is not proof of a successful remote call. A missing key or either demo-mode flag prevents live verification.

Once you have configured a valid key and a usable account, you can explicitly run a live probe, which sends a request and may incur model charges:

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

A successful probe must return model content. Match it to the request in the OrcaRouter console to verify the full path. The static GitHub Pages demo and the restricted `start-public-demo` mode do not automatically switch to live calls.

## 4. Rollback and repeat setup

The local backup may contain credentials; keep it private. To restore the previous configuration, run this from the project root and restart the backend:

```powershell
if (-not (Test-Path -LiteralPath .env.before-orcarouter)) {
  throw "No pre-OrcaRouter configuration backup exists."
}
Copy-Item -LiteralPath .env.before-orcarouter -Destination .env -Force
```

If there was no previous `.env`, set `DEMO_MODE=true` locally to return to demo mode. You can rerun the generic setup script later; preserve the existing backup before repeating the backup step.

## Partnership and verification status

Observed in the partner dashboard on 2026-09-06: the referral program is approved and the referral link is active; the open-source listing awaits manual publication and no app ID has been issued. This guide uses API-key configuration; PKCE login and device authorization are not implemented here. A live API call has not been verified. Directory publication, referral approval, and API connectivity are separate states.

## Official references

- [Quickstart](https://docs.orcarouter.ai/getting-started/quickstart)
- [OpenAI SDK compatibility](https://docs.orcarouter.ai/compatibility/openai-sdk)
