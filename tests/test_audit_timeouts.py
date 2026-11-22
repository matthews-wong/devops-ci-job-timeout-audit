import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_timeouts  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class AuditWorkflowTest(unittest.TestCase):
    def test_compliant_workflow_has_no_findings(self):
        self.assertEqual(audit_timeouts.audit_workflow(FIXTURES / "good.yml", 30), [])

    def test_missing_timeout_names_the_job(self):
        findings = audit_timeouts.audit_workflow(FIXTURES / "missing.yml", 30)
        self.assertEqual(len(findings), 1)
        self.assertIn("job 'build' has no timeout-minutes", findings[0])

    def test_timeout_above_ceiling_is_flagged(self):
        findings = audit_timeouts.audit_workflow(FIXTURES / "too-long.yml", 30)
        self.assertIn("360", findings[0])

    def test_ceiling_is_configurable(self):
        self.assertEqual(
            audit_timeouts.audit_workflow(FIXTURES / "too-long.yml", 360), []
        )


class MainTest(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual(audit_timeouts.main([str(FIXTURES / "good.yml")]), 0)
        self.assertEqual(audit_timeouts.main([str(FIXTURES / "missing.yml")]), 1)


if __name__ == "__main__":
    unittest.main()
