from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_ops.config.loader import ConfigError, load_config


class ConfigLoaderTests(unittest.TestCase):
    def test_loads_example_config_with_safe_defaults(self) -> None:
        config = load_config(Path("config.example.yaml"))

        self.assertEqual(config.mode, "report_only")
        self.assertEqual(config.workspace.data_dir, Path(".seo-ops/data"))
        self.assertEqual(config.workspace.report_dir, Path(".seo-ops/reports"))
        self.assertEqual(config.workspace.import_dir, Path(".seo-ops/imports"))
        self.assertFalse(config.automation.safe_fixes_enabled)
        self.assertFalse(config.automation.publishing_enabled)
        self.assertEqual(config.sites[0].domain, "example.com")

    def test_rejects_publishing_enabled_without_required_approval(self) -> None:
        raw_config = """
workspace:
  data_dir: .seo-ops/data
  report_dir: .seo-ops/reports
mode: report_only
approvals:
  required_for:
    - deploys
automation:
  publishing:
    enabled: true
sites:
  - name: example
    domain: example.com
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(raw_config, encoding="utf-8")

            with self.assertRaisesRegex(ConfigError, "publishing"):
                load_config(path)

    def test_requires_at_least_one_site(self) -> None:
        raw_config = """
workspace:
  data_dir: .seo-ops/data
  report_dir: .seo-ops/reports
mode: report_only
sites: []
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(raw_config, encoding="utf-8")

            with self.assertRaisesRegex(ConfigError, "site"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
