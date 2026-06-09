"""Finding model shared by providers, doctor checks, and fix queues."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any

from seo_ops.core.redaction import redact_value


class Severity(IntEnum):
    CRITICAL = 40
    HIGH = 30
    MEDIUM = 20
    LOW = 10
    INFO = 0

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class Finding:
    site: str
    source: str
    title: str
    severity: Severity
    description: str
    recommendation: str
    evidence: dict[str, Any] = field(default_factory=dict)
    fix_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["severity"] = self.severity.label
        return redact_value(payload)
