"""Local-only helpdesk web app and JSON API using the Python standard library.

This is an educational workstation demo, not a multiuser production system.
Start from repository root:
    python projects/ai-helpdesk-copilot/server.py
Open http://127.0.0.1:8000/helpdesk-copilot/
"""
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from engine import assist

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
DEFAULT_DB = Path(__file__).resolve().parent / "tickets.sqlite3"
CATEGORIES = {"Identity & Access", "Networking", "Hardware", "Software", "Security", "Other"}
PRIORITIES = {"low", "medium", "high"}


def connect(db_path):
    db = sqlite3.connect(str(db_path), timeout=5)
    db.row_factory = sqlite3.Row
    db.execute(
        """CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT NOT NULL,
            category TEXT NOT NULL, priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL
        )"""
    )
    db.commit()
    return db


def get_tickets(db_path):
    with connect(db_path) as db:
        rows = db.execute(
            "SELECT id,title,description,category,priority,status,created_at "
            "FROM tickets ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [dict(row) for row in rows]


def create_ticket(db_path, record):
    if not isinstance(record, dict):
        raise ValueError("Ticket must be an object")
    title = record.get("title", "")
    description = record.get("description", "")
    category = record.get("category", "Other")
    priority = record.get("priority", "medium")
    if not isinstance(title, str) or not (3 <= len(title.strip()) <= 120):
        raise ValueError("Title must be between 3 and 120 characters")
    if not isinstance(description, str) or len(description) > 1200:
        raise ValueError("Description must be at most 1200 characters")
    if category not in CATEGORIES or priority not in PRIORITIES:
        raise ValueError("Unknown ticket category or priority")
    created_at = datetime.now(timezone.utc).isoformat()
    with connect(db_path) as db:
        cursor = db.execute(
            "INSERT INTO tickets(title,description,category,priority,status,created_at) "
            "VALUES(?,?,?,?,?,?)",
            (title.strip(), description.strip(), category, priority, "open", created_at)
        )
        ticket_id = cursor.lastrowid
        row = db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        db.commit()
    return dict(row)


def close_ticket(db_path, ticket_id):
    with connect(db_path) as db:
        cursor = db.execute(
            "UPDATE tickets SET status='closed' WHERE id=? AND status='open'",
            (ticket_id,)
        )
        db.commit()
        return bool(cursor.rowcount)


class AppHandler(SimpleHTTPRequestHandler):
    db_path = DEFAULT_DB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, payload, status=200):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def local_request(self):
        """Limit the API to pages served from this same local development origin."""
        port = self.server.server_port
        host = self.headers.get("Host", "")
        if host not in {"127.0.0.1:" + str(port), "localhost:" + str(port)}:
            self.send_json({"error": "Local host required"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in {
            "http://127.0.0.1:" + str(port), "http://localhost:" + str(port)
        }:
            self.send_json({"error": "Same-origin requests only"}, 403)
            return False
        return True

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid request length") from None
        if not 0 < length <= 8192:
            raise ValueError("Request must be between 1 and 8192 bytes")
        try:
            value = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            raise ValueError("Invalid JSON") from None
        if not isinstance(value, dict):
            raise ValueError("Expected a JSON object")
        return value

    def do_GET(self):
        if self.path.startswith("/api/"):
            if not self.local_request():
                return
            if self.path == "/api/health":
                return self.send_json({
                    "status": "ok",
                    "server": "local",
                    "ollama_enabled": os.environ.get("HELPDESK_USE_OLLAMA") == "1",
                    "notice": "Use only fictional support data in this educational demo.",
                })
            if self.path == "/api/tickets":
                return self.send_json({"tickets": get_tickets(self.db_path)})
            return self.send_json({"error": "Unknown API route"}, 404)
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/helpdesk-copilot/")
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if not self.local_request():
            return
        try:
            payload = self.read_json()
            if self.path == "/api/assist":
                return self.send_json(assist(payload.get("question")))
            if self.path == "/api/tickets":
                return self.send_json(
                    {"ticket": create_ticket(self.db_path, payload)}, 201
                )
            match = re.fullmatch(r"/api/tickets/([0-9]+)/close", self.path)
            if match:
                changed = close_ticket(self.db_path, int(match.group(1)))
                return self.send_json({"closed": changed}, 200 if changed else 404)
            return self.send_json({"error": "Unknown API route"}, 404)
        except ValueError as exc:
            return self.send_json({"error": str(exc)}, 400)


def make_server(port=8000, db_path=DEFAULT_DB):
    """Bind only to loopback. Never expose this demo to a network or internet."""
    handler = type("BoundHelpdeskHandler", (AppHandler,), {"db_path": Path(db_path)})
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


if __name__ == "__main__":
    port = int(os.environ.get("HELPDESK_PORT", "8000"))
    with make_server(port) as server:
        print("Helpdesk Copilot: http://127.0.0.1:" + str(server.server_port) + "/helpdesk-copilot/")
        print("All tickets stay in a local SQLite file. Do NOT enter real customer data.")
        if os.environ.get("HELPDESK_USE_OLLAMA") == "1":
            print("Local Ollama mode requested; falls back to knowledge guidance if unavailable.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
