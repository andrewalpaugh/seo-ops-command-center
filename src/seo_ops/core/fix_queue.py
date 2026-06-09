"""Structured fix queue persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from seo_ops.core.findings import Finding


@dataclass
class FixQueue:
    findings: list[Finding] = field(default_factory=list)

    def prioritized(self) -> list[Finding]:
        return sorted(self.findings, key=lambda finding: int(finding.severity), reverse=True)

    def to_dict(self) -> dict[str, object]:
        return {
            "version": 1,
            "findings": [finding.to_dict() for finding in self.prioritized()],
        }

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
