# Contributing

Thanks for taking interest in this project.

## Before You Start

- Read [README.md](README.md) or [README_EN.md](README_EN.md) first.
- Use the local demo mode if you do not have an API key yet.
- Run the compatibility check before reporting provider-related issues.

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python scripts\check_model_config.py
.\.venv\Scripts\python -m pytest -vv
```

## Suggested Contribution Areas

- improve emotional support and study guidance quality
- expand provider compatibility or model integration docs
- improve web experience and accessibility
- add safety checks, escalation rules, or better risk handling
- improve testing coverage

## Pull Request Notes

- keep changes focused and easy to review
- avoid committing secrets or real API keys
- update docs if the runtime behavior changes
- include tests when you change backend logic
