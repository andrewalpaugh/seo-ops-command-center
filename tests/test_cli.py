from __future__ import annotations

import io
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
            self.assertEqual(report["sites"][0]["domain"], "example.com")
            self.assertFalse(report["automation"]["publishing_enabled"])


if __name__ == "__main__":
    unittest.main()
