import os
import tempfile
import unittest
from junction_scout import format_summary, get_link_target, scan_directory


class TestJunctionScout(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="scout_test_")

    def tearDown(self):
        try:
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)
        except Exception:
            pass

    def test_scan_empty_directory(self):
        issues = scan_directory(self.test_dir)
        self.assertEqual(issues, [])
        summary = format_summary(issues)
        self.assertEqual(summary, {})

    def test_scan_invalid_path(self):
        issues = scan_directory("Z:\\NonExistentPath\\123456")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["type"], "INVALID_PATH")

    def test_format_summary(self):
        sample = [
            {"type": "BROKEN_JUNCTION", "path": "p1"},
            {"type": "BROKEN_JUNCTION", "path": "p2"},
            {"type": "RECURSIVE_LOOP", "path": "p3"},
        ]
        s = format_summary(sample)
        self.assertEqual(s.get("BROKEN_JUNCTION"), 2)
        self.assertEqual(s.get("RECURSIVE_LOOP"), 1)


if __name__ == "__main__":
    unittest.main()
