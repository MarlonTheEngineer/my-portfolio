import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ticket_tracker import add_ticket, list_tickets, close_ticket, ticket_stats

class HelpdeskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / "tickets.db")
    def tearDown(self):
        self.temp.cleanup()
    def test_ticket_lifecycle(self):
        ticket_id = add_ticket(self.db, "Reset user login", "access", "high")
        self.assertEqual(len(list_tickets(self.db, "open")), 1)
        self.assertEqual(ticket_stats(self.db)["high_priority_open"], 1)
        self.assertTrue(close_ticket(self.db, ticket_id))
        self.assertFalse(close_ticket(self.db, ticket_id))
        self.assertEqual(ticket_stats(self.db)["closed"], 1)
    def test_invalid_title(self):
        with self.assertRaises(ValueError):
            add_ticket(self.db, " ")
    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            add_ticket(self.db, "Test", priority="urgent")

if __name__ == "__main__":
    unittest.main()
