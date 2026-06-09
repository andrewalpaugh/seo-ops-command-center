from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_ops.core.findings import Finding, Severity
from seo_ops.core.fix_queue import FixQueue


class FixQueueTests(unittest.TestCase):
    def test_saves_prioritized_findings_without_secrets(self) -> None:
        queue = FixQueue(
            findings=[
                Finding(
                    site="example.com",
                    source="doctor",
                    title="Missing approval gate",
                    severity=Severity.HIGH,
                    description="token=abc123 password: private",
                    recommendation="Require approval before deploys.",
                ),
                Finding(
                    site="example.com",
                    source="doctor",
                    title="Safe default",
                    severity=Severity.LOW,
                    description="Report-only mode is enabled.",
                    recommendation="No action needed.",
                ),
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fix_queue.json"
            queue.save(path)
            contents = path.read_text(encoding="utf-8")

        self.assertLess(contents.index("Missing approval gate"), contents.index("Safe default"))
        self.assertNotIn("private", contents)
        self.assertIn("[REDACTED]", contents)


if __name__ == "__main__":
    unittest.main()
