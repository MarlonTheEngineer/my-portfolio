# AI Helpdesk Copilot

[**Live GitHub Pages demo**](https://marlontheengineer.github.io/my-portfolio/helpdesk-copilot/) | [**Obsidian-style build notes**](notes/00%20-%20Start%20Here.md)

An educational support workflow prototype with **source-backed troubleshooting**, **ticket management**, and **optional local generative AI**. It is designed as a portfolio learning project, not a production helpdesk service.

## Two ways to run it

| Feature | Free GitHub Pages demo | Local Python server |
| --- | --- | --- |
| Search curated troubleshooting articles | Yes | Yes |
| Suggested steps with exact article IDs | Yes, rule-based retrieval | Yes, rule-based retrieval |
| Practice ticket queue | Yes, temporary browser memory | Yes, persistent SQLite |
| Generative AI language-model answers | **No** | Optional with local Ollama |
| Requires a hosted backend or paid API | No | No |
| Safe for real confidential support information | **No** | **No, educational prototype only** |

The public demo is intentionally transparent: it does **not** pretend its deterministic knowledge retrieval is a language model. Local AI generation must be enabled deliberately.

## Quick start: published browser demo

Open https://marlontheengineer.github.io/my-portfolio/helpdesk-copilot/

1. Click **Account locked**, **VPN failure**, or **Printer offline**, or type a fictional technical problem.
2. Click **Find guidance**. Read the cited source articles in the evidence panel.
3. Open the knowledge articles to inspect the full checklists and safety warnings.
4. Create a practice incident and mark it closed. In this mode, sample tickets reset on refresh.

No npm, cloud account, Vercel, Docker, or server is needed.

## Run the complete local app (Python 3.10+)

From a terminal in the downloaded or cloned repository:

~~~powershell
git clone https://github.com/MarlonTheEngineer/my-portfolio.git
cd my-portfolio
python projects/ai-helpdesk-copilot/server.py
~~~

Open **http://127.0.0.1:8000/helpdesk-copilot/**.

The Python standard-library server serves the same website and enables a same-origin local JSON API. Your practice tickets are saved in a file named **projects/ai-helpdesk-copilot/tickets.sqlite3**, which is ignored by Git. You can stop the server using Ctrl+C.

If port 8000 is taken, in PowerShell:

~~~powershell
$env:HELPDESK_PORT = "8765"
python projects/ai-helpdesk-copilot/server.py
~~~

Then open http://127.0.0.1:8765/helpdesk-copilot/.

## Optional: use a local Ollama model

Ollama is a separate optional installation. The local app works without it.

1. Install Ollama from its official website and ensure it is running.
2. Download a supported small model. Example:

~~~powershell
ollama pull llama3.2:3b
~~~

3. In a **PowerShell terminal** at the repository root:

~~~powershell
$env:HELPDESK_USE_OLLAMA = "1"
$env:HELPDESK_MODEL = "llama3.2:3b"
python projects/ai-helpdesk-copilot/server.py
~~~

4. Ask a fictional troubleshooting question in http://127.0.0.1:8000/helpdesk-copilot/.

When Ollama responds, the reply is labeled **LOCAL AI · REVIEW OUTPUT** and the matching articles appear in the evidence panel. If Ollama is unavailable, the assistant falls back to rule-based sourced guidance. Model output can be incorrect, so verify every recommendation.

**Privacy:** Ollama requests from this prototype go to **127.0.0.1:11434**. There is no external AI endpoint in the code. Only synthetic training material should be entered; this code has not been audited for production security.

## How it is built

~~~mermaid
flowchart TD
    Browser["Web interface (HTML/CSS/JS)"] --> KB["Shared knowledge.json"]
    Browser -->|"GitHub Pages demo"| BrowserSearch["Local keyword ranking"]
    Browser -->|"Localhost only"| API["Python HTTP API"]
    API --> Engine["engine.py retrieval"]
    Engine --> KB
    API --> SQLite["SQLite practice tickets"]
    Engine -->|"Only when opted in"| Ollama["Ollama at 127.0.0.1:11434"]
~~~

- **docs/helpdesk-copilot/index.html:** website layout, forms, ticket queue, accessible landmarks.
- **docs/helpdesk-copilot/styles.css:** visual design and responsive breakpoints.
- **docs/helpdesk-copilot/app.js:** browser interaction, matched article retrieval, ephemeral sample tickets.
- **docs/helpdesk-copilot/knowledge.json:** ten original synthetic helpdesk runbooks.
- **engine.py:** source matching, deterministic suggested checklists, optional local Ollama prompt.
- **server.py:** localhost-only HTTP API and SQLite persistence.
- **tests/test_copilot.py:** unit/integration tests for retrieval, ticket validation, safe SQL, and API.
- **notes/:** Markdown teaching notes formatted for Obsidian.

## Available API endpoints (local server only)

| Method | Route | Purpose |
| --- | --- | --- |
| GET | /api/health | Local server status and AI opt-in setting |
| GET | /api/tickets | Last 50 tickets |
| POST | /api/tickets | Save a fictional ticket |
| POST | /api/tickets/{id}/close | Close an open ticket |
| POST | /api/assist | Return troubleshooting guidance and exact sources |

## Test it

Run from the repository root:

~~~powershell
python -m unittest discover -s projects/ai-helpdesk-copilot/tests -v
python scripts/check_site.py
~~~

GitHub Actions runs these tests on Python 3.11 and 3.12 after changes.

## Limitations and future improvements

- Keyword overlap is not semantic vector search: different words for the same symptom can be missed. An unmatched question gives a cautious fallback.
- This prototype has no authentication, user accounts, authorization tiers, or audit trail. **Do not expose the local server to the internet or enterprise networks.**
- The public demo does not persist tickets and is not an AI LLM service. The optional local model is a separate feature.
- A production project would require secure identity, permissions, HTTPS, reliable data lifecycle, server hardening, and controlled logging.
- Future learning tasks: add custom KB editing, semantic search, source quality evaluations, redacted audit logs, role controls, and a user acceptance test.

## Notes for interviews

Describe this as a **source-grounded helpdesk prototype with optional on-device AI**, not a deployed enterprise AI agent. You can explain how the same JSON knowledge base supports both the public demo and local Python server, and demonstrate tests before describing its limitations.

The project builds on the user's earlier [Helpdesk Ticket Tracker](../helpdesk-ticket-cli/README.md), while keeping that original CLI project unchanged.
