from __future__ import annotations

import os
from typing import Optional

from fastapi import Header, HTTPException, status


def is_auth_enabled() -> bool:
    return os.getenv("API_KEY_AUTH_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


def get_configured_keys() -> set[str]:
    raw = os.getenv("API_MASTER_KEYS", "").strip()
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}


def verify_api_key(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Enterprise API key verification dependency.
    If auth is disabled (default in dev/demo), silently passes.
    If auth is enabled, verifies Bearer token or X-API-Key against API_MASTER_KEYS.
    """
    if not is_auth_enabled():
        return "anonymous-dev"

    token: Optional[str] = None
    if x_api_key:
        token = x_api_key.strip()
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    valid_keys = get_configured_keys()
    if not token or (valid_keys and token not in valid_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid API Key required in X-API-Key or Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token
