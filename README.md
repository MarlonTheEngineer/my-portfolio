# Marlon Taylor | Technical Portfolio

[**Visit the live portfolio**](https://marlontheengineer.github.io/my-portfolio/) | [GitHub profile](https://github.com/MarlonTheEngineer)

A lightweight, responsive HTML/CSS portfolio hosted using **GitHub Pages**. This repository also contains two Python utilities, a from-scratch JavaScript neural network, and an AI Helpdesk Copilot with a browser-only demo and optional local Python backend.

## Structure

| Path | Description |
| --- | --- |
| `docs/index.html` | Portfolio content and navigation |
| `docs/styles.css` | Layout, responsive styles, typography |
| `projects/helpdesk-ticket-cli/` | Python + SQLite support ticket tracker |
| `projects/log-analyzer/` | Python parser for synthetic security logs |
| `docs/neural-network/` | Live neural network training, interactive demo, and tests |
| `projects/neural-network-playground/` | Neural network documentation and learning plan |
| `docs/helpdesk-copilot/` | Interactive helpdesk browser demo and shared knowledge base |
| `projects/ai-helpdesk-copilot/` | Local Python API, SQLite tickets, unit tests, Obsidian-style notes |
| `scripts/check_site.py` | Automated static-site quality checks |
| `.github/workflows/python-tests.yml` | Python tests and website validation |

The website is served from `main` → `/docs` via GitHub Pages. Changes pushed to `main` automatically trigger a Pages build. No Node.js, React, or npm dependencies are required.

## Preview on a computer

Clone the repository, then:

```powershell
cd my-portfolio
python -m http.server 8000 --directory docs
```

Open http://localhost:8000/ and press Ctrl+C in the terminal to stop the local server. Python 3.10+ is recommended.

## Run quality checks

```powershell
python scripts/check_site.py
python -m unittest discover -s projects/helpdesk-ticket-cli/tests -v
python -m unittest discover -s projects/log-analyzer/tests -v
node --test docs/neural-network/tests.js
python -m unittest discover -s projects/ai-helpdesk-copilot/tests -v
```

Automated checks run in GitHub Actions when portfolio or project files change.

## Git exercise

```powershell
git clone https://github.com/MarlonTheEngineer/my-portfolio.git
cd my-portfolio
git switch -c feature/my-update
# Edit docs/index.html, then:
git diff
git add docs/index.html
git commit -m "docs: update portfolio introduction"
git push -u origin feature/my-update
```

Open a pull request on GitHub, review changes, and merge it.

## Project details

- [Helpdesk Ticket Tracker](projects/helpdesk-ticket-cli/README.md): create, close, list and summarize local SQLite tickets.
- [Security Log Analyzer](projects/log-analyzer/README.md): parse a documented practice log format, count severities, and report source IPs.
- [Neural Network Playground](projects/neural-network-playground/README.md): [live interactive demo](https://marlontheengineer.github.io/my-portfolio/neural-network/) of a neural network training on synthetic patterns, including model code, browser UI, and automated tests.
- [AI Helpdesk Copilot](projects/ai-helpdesk-copilot/README.md): [live interactive support demo](https://marlontheengineer.github.io/my-portfolio/helpdesk-copilot/) with source-backed troubleshooting, local-only Python/SQLite mode, optional Ollama, and [Obsidian notes](projects/ai-helpdesk-copilot/notes/00%20-%20Start%20Here.md).

These are **learning projects**, not production security or helpdesk systems. Avoid committing secrets, real ticket data, user information, or production logs.

## Deployment

Published site: https://marlontheengineer.github.io/my-portfolio/

If deployment stops working, check **Actions** and **Settings → Pages** in this repository. GitHub Pages should use branch `main` and folder `/docs`.
