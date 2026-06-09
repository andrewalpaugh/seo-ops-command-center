from __future__ import annotations

import unittest

from seo_ops.core.redaction import redact_mapping, redact_string


class RedactionTests(unittest.TestCase):
    def test_redacts_known_secret_patterns_from_strings(self) -> None:
        text = "token=abc123 GOOGLE_CLIENT_SECRET=super-secret password: hunter2"

        redacted = redact_string(text)

        self.assertNotIn("super-secret", redacted)
        self.assertNotIn("hunter2", redacted)
        self.assertIn("[REDACTED]", redacted)

    def test_redacts_secret_keys_recursively(self) -> None:
        payload = {
            "site": "example.com",
            "api_key": "secret-key",
            "nested": {"password": "secret-password", "safe": "value"},
        }

        redacted = redact_mapping(payload)

        self.assertEqual(redacted["site"], "example.com")
        self.assertEqual(redacted["api_key"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["password"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["safe"], "value")


if __name__ == "__main__":
    unittest.main()
