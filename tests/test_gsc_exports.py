from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from seo_ops.config.schema import (
    ApprovalConfig,
    AutomationConfig,
    SeoOpsConfig,
    SiteConfig,
    WorkspaceConfig,
)
from seo_ops.providers.gsc_exports import collect_gsc_export_findings


class GscExportProviderTests(unittest.TestCase):
    def test_finds_low_ctr_pages_from_performance_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import_dir = Path(tmp) / "imports"
            site_dir = import_dir / "gsc" / "example.com"
            site_dir.mkdir(parents=True)
            _write_csv(
                site_dir / "performance-pages.csv",
                ["Top pages", "Clicks", "Impressions", "CTR", "Position"],
                [
                    ["https://example.com/high-impression-low-ctr/", "8", "2500", "0.3%", "7.2"],
                    ["https://example.com/healthy/", "200", "3000", "6.7%", "3.1"],
                ],
            )
            config = _config(import_dir)

            findings = collect_gsc_export_findings(config)

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.site, "example.com")
        self.assertEqual(finding.source, "gsc_export")
        self.assertEqual(finding.title, "Page has high impressions and low CTR")
        self.assertEqual(finding.evidence["url"], "https://example.com/high-impression-low-ctr/")
        self.assertEqual(finding.evidence["impressions"], 2500)
        self.assertEqual(finding.evidence["ctr"], 0.003)

    def test_unrecognized_csv_shape_creates_warning_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import_dir = Path(tmp) / "imports"
            site_dir = import_dir / "gsc" / "example.com"
            site_dir.mkdir(parents=True)
            _write_csv(site_dir / "unknown.csv", ["Unexpected", "Columns"], [["value", "value"]])
            config = _config(import_dir)

            findings = collect_gsc_export_findings(config)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].site, "example.com")
        self.assertEqual(findings[0].title, "Unrecognized GSC export")
        self.assertEqual(findings[0].evidence["file"], "unknown.csv")


def _config(import_dir: Path) -> SeoOpsConfig:
    return SeoOpsConfig(
        workspace=WorkspaceConfig(
            data_dir=Path(".seo-ops/data"),
            report_dir=Path(".seo-ops/reports"),
            import_dir=import_dir,
        ),
        mode="report_only",
        approvals=ApprovalConfig(),
        automation=AutomationConfig(),
        sites=(
            SiteConfig(
                name="example",
                domain="example.com",
                providers={"gsc_exports": {"enabled": True}},
            ),
        ),
    )


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
