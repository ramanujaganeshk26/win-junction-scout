import unittest
import os
from junction_scout import scan_directory

class TestJunctionScout(unittest.TestCase):
    def test_scan_empty(self):
        issues = scan_directory(r".")
        self.assertIsInstance(issues, list)

if __name__ == "__main__":
    unittest.main()
