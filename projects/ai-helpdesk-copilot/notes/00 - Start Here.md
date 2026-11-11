---
tags: [portfolio, ai, helpdesk, python, javascript, study-notes]
type: moc
status: build-complete
---
# AI Helpdesk Copilot | Start Here

> [!summary] The idea in plain English
> I built a helpdesk practice program where someone describes a computer problem, the program finds matching troubleshooting instructions, and it shows exactly where those instructions came from. I can also create and close sample support tickets. An optional local AI model can write answers using the retrieved articles.

**Live demo:** https://marlontheengineer.github.io/my-portfolio/helpdesk-copilot/

**GitHub source:** https://github.com/MarlonTheEngineer/my-portfolio/tree/main/projects/ai-helpdesk-copilot

**Important distinction:** The public website uses keyword search and predefined articles, not a generative AI language model. The optional Ollama component runs locally on my own computer.

## My learning map

1. [[01 - What the Project Actually Does]]
2. [[02 - How We Built It]]
3. [[03 - Running and Operating the App]]
4. [[04 - The Code Explained]]
5. [[05 - Security and Testing]]
6. [[06 - My Practice Exercises]]

## The whole system in one diagram

~~~mermaid
flowchart LR
    A["Type a fictional IT problem"] --> B["Find matching KB articles"]
    B --> C["Show suggested checklist + article IDs"]
    C --> D["Human verifies and decides"]
    A --> E["Optional local Ollama"]
    B --> E
    E --> C
    F["Create practice ticket"] --> G["Demo: memory"]
    F --> H["Local server: SQLite"]
~~~

## What makes this a useful portfolio project?

- Frontend development: an interactive website and responsive styling.
- Backend development: a local Python HTTP API.
- Databases: saving structured helpdesk tickets with SQLite.
- Information retrieval: ranking articles against a question.
- Applied AI: optional local model answers with supporting sources.
- Software quality: input validation, automated tests, and clear limitations.

## First thing to try

1. Open the live demo and choose **VPN failure**.
2. Look at the evidence panel. The assistant should find the VPN article.
3. Open the source checklist and compare it with the answer.
4. Create a fictional ticket, close it, then refresh to observe demo storage limitations.
5. Read [[02 - How We Built It]] to understand how each part works.

> [!warning] Practice environment
> Do not input real passwords, personal information, or confidential support tickets. It is not a production helpdesk tool.
