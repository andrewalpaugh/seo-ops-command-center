from __future__ import annotations

import io
import csv
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from seo_ops.cli import main


class CliTests(unittest.TestCase):
    def test_doctor_validates_example_config(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["doctor", "--config", "config.example.yaml"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Configuration OK", output.getvalue())
        self.assertIn("report_only", output.getvalue())

    def test_report_only_run_writes_report_and_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "run",
                        "--config",
                        "config.example.yaml",
                        "--mode",
                        "report-only",
                        "--output-dir",
                        tmp,
                    ]
                )

            report_path = Path(tmp) / "report.json"
            queue_path = Path(tmp) / "fix_queue.json"

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(queue_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "report_only")
            self.assertEqual(report["workspace"]["import_dir"], ".seo-ops/imports")
            self.assertEqual(report["sites"][0]["domain"], "example.com")
            self.assertFalse(report["automation"]["publishing_enabled"])

    def test_report_only_run_includes_gsc_export_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            import_dir = tmp_path / "imports"
            site_dir = import_dir / "gsc" / "example.com"
            site_dir.mkdir(parents=True)
            with (site_dir / "performance-pages.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Top pages", "Clicks", "Impressions", "CTR", "Position"])
                writer.writerow(["https://example.com/low-ctr/", "2", "1500", "0.2%", "8.4"])
            config_path = tmp_path / "config.yaml"
            config_path.write_text(
                f"""
workspace:
  data_dir: {tmp_path / "data"}
  report_dir: {tmp_path / "reports"}
  import_dir: {import_dir}
mode: report_only
sites:
  - name: example
    domain: example.com
    providers:
      gsc_exports:
        enabled: true
""",
                encoding="utf-8",
            )
            output_dir = tmp_path / "output"

            with redirect_stdout(io.StringIO()):
                exit_code = main(
                    [
                        "run",
                        "--config",
                        str(config_path),
                        "--mode",
                        "report-only",
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            queue = json.loads((output_dir / "fix_queue.json").read_text(encoding="utf-8"))
            titles = [finding["title"] for finding in queue["findings"]]

        self.assertEqual(exit_code, 0)
        self.assertIn("Page has high impressions and low CTR", titles)


if __name__ == "__main__":
    unittest.main()
