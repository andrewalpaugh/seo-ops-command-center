"""Parse local Google Search Console CSV exports into findings."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from seo_ops.config.schema import SeoOpsConfig, SiteConfig
from seo_ops.core.findings import Finding, Severity


LOW_CTR_IMPRESSIONS_THRESHOLD = 1000
LOW_CTR_THRESHOLD = 0.01


def collect_gsc_export_findings(config: SeoOpsConfig) -> list[Finding]:
    findings: list[Finding] = []
    for site in config.sites:
        if not _provider_enabled(site):
            continue
        site_dir = config.workspace.import_dir / "gsc" / site.domain
        if not site_dir.exists():
            continue
        for csv_path in sorted(site_dir.glob("*.csv")):
            findings.extend(_findings_for_csv(site, csv_path))
    return findings


def _findings_for_csv(site: SiteConfig, csv_path: Path) -> list[Finding]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [_unrecognized_export(site, csv_path, [])]
        headers = [header.strip() for header in reader.fieldnames]
        rows = list(reader)

    if _is_performance_pages_export(headers):
        return _performance_page_findings(site, csv_path, rows)
    return [_unrecognized_export(site, csv_path, headers)]


def _performance_page_findings(site: SiteConfig, csv_path: Path, rows: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for row in rows:
        url = _string(row, "Top pages", "Page", "URL")
        impressions = _integer(row, "Impressions")
        ctr = _percent(row, "CTR")
        if not url or impressions is None or ctr is None:
            continue
        if impressions >= LOW_CTR_IMPRESSIONS_THRESHOLD and ctr < LOW_CTR_THRESHOLD:
            findings.append(
                Finding(
                    site=site.domain,
                    source="gsc_export",
                    title="Page has high impressions and low CTR",
                    severity=Severity.MEDIUM,
                    description=(
                        f"{url} has {impressions} impressions but a CTR below "
                        f"{LOW_CTR_THRESHOLD:.0%} in the imported GSC performance export."
                    ),
                    recommendation="Review the title, meta description, search intent fit, and SERP competition for this page.",
                    evidence={
                        "file": csv_path.name,
                        "url": url,
                        "impressions": impressions,
                        "ctr": ctr,
                        "thresholds": {
                            "minimum_impressions": LOW_CTR_IMPRESSIONS_THRESHOLD,
                            "maximum_ctr": LOW_CTR_THRESHOLD,
                        },
                    },
                )
            )
    return findings


def _unrecognized_export(site: SiteConfig, csv_path: Path, headers: list[str]) -> Finding:
    return Finding(
        site=site.domain,
        source="gsc_export",
        title="Unrecognized GSC export",
        severity=Severity.LOW,
        description=f"{csv_path.name} does not match a supported Google Search Console CSV export shape.",
        recommendation="Export the Performance > Pages report as CSV, or add support for this report shape.",
        evidence={"file": csv_path.name, "headers": headers},
    )


def _is_performance_pages_export(headers: list[str]) -> bool:
    normalized = {_normalize(header) for header in headers}
    return bool({"clicks", "impressions", "ctr"} <= normalized and normalized & {"top pages", "page", "url"})


def _provider_enabled(site: SiteConfig) -> bool:
    settings = site.providers.get("gsc_exports")
    if settings is None:
        return False
    if isinstance(settings, dict):
        return settings.get("enabled") is True
    return bool(settings)


def _string(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _row_value(row, key)
        if value:
            return value.strip()
    return ""


def _integer(row: dict[str, Any], key: str) -> int | None:
    value = _row_value(row, key)
    if not value:
        return None
    try:
        return int(value.replace(",", "").strip())
    except ValueError:
        return None


def _percent(row: dict[str, Any], key: str) -> float | None:
    value = _row_value(row, key)
    if not value:
        return None
    cleaned = value.strip().replace(",", "")
    try:
        if cleaned.endswith("%"):
            return float(cleaned[:-1]) / 100
        parsed = float(cleaned)
    except ValueError:
        return None
    return parsed / 100 if parsed > 1 else parsed


def _row_value(row: dict[str, Any], key: str) -> str:
    normalized_key = _normalize(key)
    for candidate, value in row.items():
        if _normalize(candidate) == normalized_key and value is not None:
            return str(value)
    return ""


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()
