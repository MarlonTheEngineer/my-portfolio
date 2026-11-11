---
tags: [software-engineering, build-log, architecture]
---
# How We Built It: From Idea to Working Project

Return to [[00 - Start Here]] | Next: [[03 - Running and Operating the App]]

These notes describe the implementation that was added to the portfolio. It is a guided learning project, and I should be able to explain and modify each component before representing it as independent work.

## Step 1: Choose a realistic problem

**Problem:** IT technicians repeatedly answer similar issues: account lockouts, MFA troubles, VPN errors, printers, and DNS failures.

**Goal:** Give a technician a fast, reviewable starting checklist and a way to record practice work.

**Constraint:** GitHub Pages hosts static files, so the live public portfolio must work without a paid server or AI subscription.

**Design choice:** Build a useful browser-only demo first; add a localhost Python backend separately.

## Step 2: Make one shared knowledge base

File: **docs/helpdesk-copilot/knowledge.json**

We wrote ten synthetic troubleshooting runbooks. Each record includes:

- id (for example KB-004)
- title
- category
- keywords
- summary
- ordered steps
- safety warning

**Why JSON?** Both JavaScript and Python can read it easily. This prevents us from maintaining completely separate article lists.

## Step 3: Build the website

Files:

- **index.html** defines the input form, results area, article panel, and ticket workspace.
- **styles.css** creates the professional dark dashboard and mobile layout.
- **app.js** responds to clicks and forms, loads the JSON file, renders source cards, and manages temporary demo tickets.

The browser interface does not need npm, React, Vercel, or a database server.

## Step 4: Implement knowledge search

We used a simple word-overlap ranking method.

~~~mermaid
flowchart LR
    Q["User's question"] --> T["Break into words"]
    T --> S["Remove common words"]
    S --> R["Score each article"]
    R --> O["Sort by score"]
    O --> A["Show top 3 sources"]
~~~

The scoring rule is:

| Article field containing a matching word | Points |
|---|---:|
| Title | 4 |
| Keywords | 3 |
| Summary or steps | 1 |

A word can contribute points in multiple fields. The scores are heuristic ranking scores, **not** probabilities or model confidence.

This is called **keyword retrieval**, not an actual neural network or a generative AI model.

## Step 5: Create the optional Python service

File: **projects/ai-helpdesk-copilot/server.py**

The server uses Python's built-in HTTP tools and runs on **127.0.0.1** only.

It accepts browser requests for troubleshooting assistance and sample tickets and returns JSON.

The tickets are stored in a local SQLite database using parameterized queries.

## Step 6: Add optional local language-model responses

File: **projects/ai-helpdesk-copilot/engine.py**

The engine first retrieves matching articles.

If Ollama is explicitly enabled, it sends the question and retrieved article text to **127.0.0.1:11434**. It asks the model to answer from those sources and cite their IDs.

If the model is unavailable or disabled, the system uses a deterministic checklist instead.

We do not send questions to a paid hosted AI API.

## Step 7: Add validation and automated tests

File: **tests/test_copilot.py**

We test:

- matching the correct knowledge article
- safe responses when nothing matches
- input validation
- SQLite create/list/close operations
- hostile SQL-looking text stored as ordinary data
- actual HTTP API requests
- cross-origin requests being rejected

The project is included in the repository's GitHub Actions workflow.

## Step 8: Document, showcase, and publish

We added a card on the main portfolio that links to the public demo and committed the code to GitHub. GitHub Pages publishes the static version; the local Python server is not deployed.

## My biggest lesson

**A good project is not just code.** It includes a useful problem, a clear interface, documented design decisions, tests, limits, and instructions for somebody else to run it.
