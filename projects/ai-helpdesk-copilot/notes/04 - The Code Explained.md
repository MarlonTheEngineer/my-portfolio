---
tags: [code-reading, javascript, python, sqlite, retrieval]
---
# The Code Explained: Each Building Block

Return to [[00 - Start Here]] | Previous: [[03 - Running and Operating the App]]

## Building-block map

~~~mermaid
flowchart TD
    A["index.html: forms and layout"] --> B["app.js: browser events"]
    B --> C["knowledge.json: troubleshooting runbooks"]
    B --> D["server.py: localhost endpoints"]
    D --> E["engine.py: search + optional model"]
    E --> C
    E --> F["Ollama: only if enabled"]
    D --> G["SQLite: ticket persistence"]
    H["styles.css: visual design"] --> A
    I["tests/test_copilot.py"] --> D
    I --> E
~~~

## 1. knowledge.json is the content

Each KB entry has an ID, title, category, keywords, summary, steps, and caution. It is data rather than program code.

### Example idea

~~~json
{
  "id": "KB-004",
  "title": "VPN fails to connect",
  "category": "Networking"
}
~~~

The real article also contains a summary, keywords, steps, and a caution.

**Why it matters:** Source citations let me check the assistant's advice rather than blindly trusting a generated answer.

## 2. app.js is the frontend brain

The main responsibilities include:

| Function | Explanation |
|---|---|
| tokenize | Split a question into meaningful words |
| matched | Rank the runbooks by keyword overlap |
| guided | Turn the best matching article into a checklist |
| renderSources | Display retrieved sources as accessible cards |
| renderArticles | Build the searchable article library |
| ask | Use the local API if available or fall back to browser guidance |
| createTicket | Create a fictional ticket |
| renderTickets | Display statuses and close buttons |
| init | Load the shared knowledge and detect the local server |

User-entered strings are inserted as **textContent**, not raw HTML. This reduces the chance that ticket titles turn into executable markup.

## 3. engine.py handles sourced guidance

### Ranking articles

It splits the question into words and gives more points for a word in a title or keyword than the article body.

~~~text
Article title match       +4
Article keyword match     +3
Article body match        +1
~~~

It sorts by score and returns up to three articles.

### Deterministic versus generated answer

**guided_answer:** formats an existing source checklist; it does not invent steps.

**ollama_answer:** optionally sends the question and retrieved article text to a local language model. The prompt asks the model to rely on the supplied articles, but it can still make errors.

**assist:** coordinates retrieval, optional AI, and exact source IDs.

## 4. server.py is the local backend

~~~mermaid
sequenceDiagram
  participant User
  participant Browser
  participant Python as Local Python server
  participant DB as SQLite
  User->>Browser: Create practice ticket
  Browser->>Python: POST /api/tickets
  Python->>DB: INSERT validated title, priority, category
  DB-->>Python: New ticket row
  Python-->>Browser: JSON response
  Browser-->>User: Updated ticket queue
~~~

The routes are:

- GET /api/health
- GET /api/tickets
- POST /api/tickets
- POST /api/tickets/{id}/close
- POST /api/assist

The server binds to **127.0.0.1**, so it is intended to be run on the same computer as the browser, not deployed to a public host.

## 5. SQLite stores support tickets

The table stores a ticket ID, title, description, category, priority, status, and created-at time.

It uses **parameterized SQL placeholders** so submitted values are treated as data rather than executable SQL syntax.

The database is created locally the first time it is needed.

## 6. HTML and CSS define the presentation

- index.html contains the hero, questions, evidence panel, ticket form, and article catalog.
- styles.css sets typography, spacing, contrast, and responsive layouts.
- All dependencies are local to the site. No npm build or deployment service is required.

## 7. The tests prove key behaviors

Tests verify that an account lockout query points to KB-001, that an unknown question is not assigned a fake answer, that tickets can be closed, and that a cross-origin API request is rejected.

## My takeaway

**Frontend shows information. Backend manages data. Knowledge base supplies evidence. AI is optional. Automated tests check assumptions.**
