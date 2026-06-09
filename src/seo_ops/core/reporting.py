"""Report-only run output."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from seo_ops.config.schema import SeoOpsConfig
from seo_ops.core.fix_queue import FixQueue
from seo_ops.core.findings import Finding, Severity
from seo_ops.core.redaction import redact_value
from seo_ops.providers.gsc_exports import collect_gsc_export_findings


def build_doctor_findings(config: SeoOpsConfig) -> list[Finding]:
    findings: list[Finding] = []
    if config.mode == "report_only":
        findings.append(
            Finding(
                site="workspace",
                source="doctor",
                title="Report-only mode enabled",
                severity=Severity.INFO,
                description="The workspace is configured to avoid production mutations by default.",
                recommendation="No action needed.",
            )
        )
    if not config.automation.publishing_enabled:
        findings.append(
            Finding(
                site="workspace",
                source="doctor",
                title="Publishing disabled",
                severity=Severity.INFO,
                description="Publishing automation is disabled.",
                recommendation="Enable only in advanced mode with explicit approval gates.",
            )
        )
    for site in config.sites:
        if not site.providers:
            findings.append(
                Finding(
                    site=site.domain,
                    source="doctor",
                    title="No providers configured",
                    severity=Severity.LOW,
                    description="This site has no provider integrations configured.",
                    recommendation="Add GSC, PageSpeed, or vendor alert providers when ready.",
                )
            )
    return findings


def write_report_only_run(config: SeoOpsConfig, output_dir: str | Path) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    queue = FixQueue([*build_doctor_findings(config), *collect_gsc_export_findings(config)])
    queue_path = output_path / "fix_queue.json"
    report_path = output_path / "report.json"
    queue.save(queue_path)

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "report_only",
        "workspace": {
            "data_dir": str(config.workspace.data_dir),
            "report_dir": str(config.workspace.report_dir),
            "import_dir": str(config.workspace.import_dir),
        },
        "automation": {
            "safe_fixes_enabled": config.automation.safe_fixes_enabled,
            "content_generation_enabled": config.automation.content_generation_enabled,
            "content_generation_mode": config.automation.content_generation_mode,
            "publishing_enabled": config.automation.publishing_enabled,
        },
        "sites": [_site_summary(site) for site in config.sites],
        "artifacts": {
            "fix_queue": str(queue_path),
        },
    }
    report_path.write_text(json.dumps(redact_value(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, queue_path


def _site_summary(site: Any) -> dict[str, Any]:
    return {
        "name": site.name,
        "domain": site.domain,
        "group": site.group,
        "ownership": site.ownership,
        "edit_policy": site.edit_policy,
        "providers": sorted(site.providers.keys()),
        "deploy": {
            "type": site.deploy.get("type"),
            "require_approval": site.deploy.get("require_approval"),
        }
        if site.deploy
        else {},
    }
