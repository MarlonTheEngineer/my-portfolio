"""Offline helpdesk tracker, using only Python's standard library."""
import argparse
import sqlite3
from datetime import datetime, timezone

def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS tickets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      category TEXT NOT NULL,
      priority TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'open',
      created_at TEXT NOT NULL,
      closed_at TEXT)""")
    db.commit()
    return db

def add_ticket(path, title, category="other", priority="medium"):
    if not title.strip():
        raise ValueError("Title must not be blank")
    if category not in {"access", "hardware", "software", "network", "other"}:
        raise ValueError("Invalid category")
    if priority not in {"low", "medium", "high"}:
        raise ValueError("Invalid priority")
    with connect(path) as db:
        cur = db.execute(
            "INSERT INTO tickets(title, category, priority, created_at) VALUES(?, ?, ?, ?)",
            (title.strip(), category, priority, datetime.now(timezone.utc).isoformat()))
        return cur.lastrowid

def list_tickets(path, status="all"):
    if status not in {"all", "open", "closed"}:
        raise ValueError("Invalid status")
    with connect(path) as db:
        if status == "all":
            rows = db.execute("SELECT * FROM tickets ORDER BY id DESC")
        else:
            rows = db.execute("SELECT * FROM tickets WHERE status=? ORDER BY id DESC", (status,))
        return [dict(row) for row in rows]

def close_ticket(path, ticket_id):
    with connect(path) as db:
        cur = db.execute(
            "UPDATE tickets SET status='closed', closed_at=? WHERE id=? AND status='open'",
            (datetime.now(timezone.utc).isoformat(), ticket_id))
        return cur.rowcount == 1

def ticket_stats(path):
    rows = list_tickets(path)
    return {"total": len(rows),
            "open": sum(r["status"] == "open" for r in rows),
            "closed": sum(r["status"] == "closed" for r in rows),
            "high_priority_open": sum(
                r["status"] == "open" and r["priority"] == "high" for r in rows)}

def main():
    parser = argparse.ArgumentParser(description="SQLite-backed helpdesk tracker")
    parser.add_argument("--db", default="tickets.db", help="Database file location")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("title")
    add.add_argument("--category", choices=["access", "hardware", "software", "network", "other"], default="other")
    add.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    listing = commands.add_parser("list")
    listing.add_argument("--status", choices=["all", "open", "closed"], default="all")
    close = commands.add_parser("close")
    close.add_argument("id", type=int)
    commands.add_parser("stats")
    args = parser.parse_args()
    if args.command == "add":
        print("Created ticket #{}".format(add_ticket(args.db, args.title, args.category, args.priority)))
    elif args.command == "list":
        for row in list_tickets(args.db, args.status):
            print("#{id} [{status}] {priority}/{category}: {title}".format(**row))
    elif args.command == "close":
        print("Ticket closed" if close_ticket(args.db, args.id) else "Ticket not found or already closed")
    else:
        for key, value in ticket_stats(args.db).items():
            print("{}: {}".format(key, value))

if __name__ == "__main__":
    main()
