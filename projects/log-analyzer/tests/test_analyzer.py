import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyzer import parse_line, analyze_lines

class AnalyzerTests(unittest.TestCase):
    def test_parse_valid_line(self):
        event = parse_line("2026-11-10T12:00:00Z ERROR src=10.0.0.5 msg=Login failed")
        self.assertEqual(event["source_ip"], "10.0.0.5")
    def test_reject_invalid_line(self):
        self.assertIsNone(parse_line("not valid"))
        self.assertIsNone(parse_line("2026-11-10T12:00:00Z ERROR src=notanip msg=No"))
    def test_summary(self):
        rows = ["2026-11-10T12:00:00Z ERROR src=10.0.0.5 msg=Login failed",
                "2026-11-10T12:01:00Z WARN src=10.0.0.5 msg=Multiple failures",
                "invalid line"]
        report = analyze_lines(rows)
        self.assertEqual(report["valid_events"], 2)
        self.assertEqual(report["malformed_lines"], 1)
        self.assertEqual(report["top_sources"][0]["events"], 2)

if __name__ == "__main__":
    unittest.main()
