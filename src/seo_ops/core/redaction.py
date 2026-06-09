"""Redaction helpers for reports, queues, logs, and fixtures."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


REDACTION = "[REDACTED]"
SECRET_KEY_PARTS = (
    "api_key",
    "app_password",
    "client_secret",
    "credential",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
)
SECRET_PATTERNS = (
    re.compile(
        r"(?i)\b([a-z0-9_ -]*(?:api[_-]?key|token|secret|password|client[_-]?secret)[a-z0-9_ -]*)"
        r"\s*[:=]\s*['\"]?[^'\"\s,}]+"
    ),
)


def redact_string(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}={REDACTION}", redacted)
    return redacted


def redact_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _redact_value(str(key), item) for key, item in value.items()}


def redact_value(value: Any) -> Any:
    return _redact_value("", value)


def _redact_value(key: str, value: Any) -> Any:
    if _is_secret_key(key):
        return REDACTION
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, Mapping):
        return redact_mapping(value)
    if isinstance(value, list):
        return [_redact_value("", item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value("", item) for item in value)
    return value


def _is_secret_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SECRET_KEY_PARTS)
