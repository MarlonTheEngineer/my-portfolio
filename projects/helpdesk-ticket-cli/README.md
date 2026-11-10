# Helpdesk Ticket Tracker

A Python command-line ticket tracking app with SQLite persistence. It demonstrates basic CRUD operations, input validation, parameterized SQL, and unit testing.

## Requirements
Python 3.10+ with no external packages.

## Run
Open PowerShell in this folder:

```powershell
python ticket_tracker.py add "Account locked" --category access --priority high
python ticket_tracker.py add "Printer offline" --category hardware
python ticket_tracker.py list
python ticket_tracker.py stats
python ticket_tracker.py close 1
python ticket_tracker.py list --status closed
```

A local `tickets.db` is created. Do not upload actual customer support data.

## Tests
```powershell
python -m unittest discover -s tests -v
```

## Next features
- Search by title and category
- Export CSV report
- Track assignee and resolution notes
- Add a web dashboard

This is a learning project, not a production helpdesk service.
