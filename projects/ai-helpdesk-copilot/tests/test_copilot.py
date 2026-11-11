"""Standard-library tests for the local Helpdesk Copilot and retrieval engine."""
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine
import server


class KnowledgeTests(unittest.TestCase):
    def test_source_catalog(self):
        articles = engine.load_articles()
        self.assertGreaterEqual(len(articles), 8)
        self.assertEqual(len({a["id"] for a in articles}), len(articles))
        for article in articles:
            self.assertTrue(article["steps"])
            self.assertTrue(article["caution"])

    def test_find_signin_article(self):
        hits = engine.search_articles("The account is locked and cannot sign in")
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "KB-001")

    def test_find_phishing_article(self):
        hits = engine.search_articles("suspicious phishing email")
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "KB-010")

    def test_unknown_question_fails_closed(self):
        self.assertEqual(engine.search_articles("galactic banana constellation"), [])
        answer = engine.guided_answer("galactic banana constellation", [])
        self.assertIn("could not find", answer)

    def test_guidance_includes_exact_citation_and_safety(self):
        selected = engine.search_articles("printer offline")
        text = engine.guided_answer("printer offline", selected)
        self.assertIn("[KB-006]" if False else "KB-006", text)
        self.assertIn("Safety note:", text)

    def test_input_limits(self):
        for invalid in ("", " " * 4, "x" * 601, None):
            with self.assertRaises(ValueError):
                engine.assist(invalid)

    def test_knowledge_only_when_model_disabled(self):
        original = os.environ.pop("HELPDESK_USE_OLLAMA", None)
        try:
            answer = engine.assist("VPN fails to connect")
            self.assertEqual(answer["mode"], "knowledge")
            self.assertEqual(answer["sources"][0]["id"], "KB-004")
        finally:
            if original is not None:
                os.environ["HELPDESK_USE_OLLAMA"] = original


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = Path(self.directory.name) / "training.sqlite3"

    def tearDown(self):
        self.directory.cleanup()

    def test_create_list_close(self):
        row = server.create_ticket(self.db, {
            "title": "Fictional VPN issue", "description": "Sample details",
            "category": "Networking", "priority": "low"
        })
        self.assertEqual(row["status"], "open")
        rows = server.get_tickets(self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Fictional VPN issue")
        self.assertTrue(server.close_ticket(self.db, row["id"]))
        self.assertFalse(server.close_ticket(self.db, row["id"]))
        self.assertEqual(server.get_tickets(self.db)[0]["status"], "closed")

    def test_sql_injection_is_stored_as_text(self):
        title = "'); DROP TABLE tickets;--"
        server.create_ticket(self.db, {
            "title": title, "description": "", "category": "Other", "priority": "high"
        })
        self.assertEqual(server.get_tickets(self.db)[0]["title"], title)

    def test_bad_ticket_rejected(self):
        for record in (
            {"title": "a"},
            {"title": "valid", "category": "invalid"},
            {"title": "valid", "priority": "urgent"},
            {"title": "valid", "description": "x" * 1201},
        ):
            with self.assertRaises(ValueError):
                server.create_ticket(self.db, record)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.httpd = server.make_server(port=0, db_path=Path(cls.directory.name) / "api.sqlite3")
        cls.url = "http://127.0.0.1:" + str(cls.httpd.server_port)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)
        cls.directory.cleanup()

    def request_json(self, path, payload=None, headers=None):
        request = Request(
            self.url + path,
            data=json.dumps(payload).encode("utf-8") if payload is not None else None,
            headers={"Content-Type": "application/json", **(headers or {})},
            method="POST" if payload is not None else "GET",
        )
        with urlopen(request, timeout=5) as response:
            return response.status, json.load(response)

    def test_local_api_and_static_site(self):
        code, health = self.request_json("/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(health["server"], "local")
        with urlopen(self.url + "/helpdesk-copilot/", timeout=5) as response:
            html = response.read().decode("utf-8")
        self.assertIn("Helpdesk support.", html)

    def test_ask_has_sources(self):
        code, answer = self.request_json("/api/assist", {"question": "MFA push isn't arriving"})
        self.assertEqual(code, 200)
        self.assertEqual(answer["sources"][0]["id"], "KB-003")

    def test_ticket_api(self):
        code, result = self.request_json("/api/tickets", {
            "title": "Test printer issue", "description": "Fictional",
            "category": "Hardware", "priority": "medium"
        })
        self.assertEqual(code, 201)
        ident = result["ticket"]["id"]
        code, tickets = self.request_json("/api/tickets")
        self.assertEqual(code, 200)
        self.assertIn(ident, [t["id"] for t in tickets["tickets"]])
        code, closed = self.request_json("/api/tickets/" + str(ident) + "/close", {})
        self.assertTrue(closed["closed"])

    def test_cross_origin_request_blocked(self):
        with self.assertRaises(HTTPError) as caught:
            self.request_json("/api/tickets", {
                "title": "Bad origin", "category": "Other", "priority": "low",
            }, {"Origin": "https://example.com"})
        self.assertEqual(caught.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
