---
tags: [runbook, python, github-pages, ollama]
---
# Running and Operating the App

Return to [[00 - Start Here]] | Previous: [[02 - How We Built It]]

## Option A: Public demo, simplest

Visit https://marlontheengineer.github.io/my-portfolio/helpdesk-copilot/

**What works:** ask practice questions, review cited knowledge, search articles, create and close temporary sample tickets.

**What does not work:** persistent SQLite tickets and a live generative AI model. The public site is a static frontend.

## Option B: Local backend, saved tickets

**Prerequisite:** Python 3.10 or newer.

~~~powershell
git clone https://github.com/MarlonTheEngineer/my-portfolio.git
cd my-portfolio
python projects/ai-helpdesk-copilot/server.py
~~~

Open **http://127.0.0.1:8000/helpdesk-copilot/**.

If Python is not recognized in Windows PowerShell, try the Windows Python launcher:

~~~powershell
py -3 projects/ai-helpdesk-copilot/server.py
~~~

Look for the label **Local server · sourced guidance** and **LOCAL SQLITE STORAGE**.

### My operating checklist

- [ ] Open the web page.
- [ ] Ask about a fictional sign-in failure.
- [ ] Read the answer and review its exact source IDs.
- [ ] Create a fictional ticket and choose a category and priority.
- [ ] Refresh the page to prove local SQLite persistence.
- [ ] Mark the ticket closed.
- [ ] Inspect the new database file and ensure it is not committed to Git.

### Troubleshooting

- **Port already in use:** PowerShell: set the port, restart, and use the new URL.

~~~powershell
$env:HELPDESK_PORT = "8765"
python projects/ai-helpdesk-copilot/server.py
~~~

- **Knowledge article missing:** make sure the full repository is downloaded and the JSON file exists at docs/helpdesk-copilot/knowledge.json.
- **No matching answer:** use more specific terms from the error message. Keyword search does not understand every synonym.
- **Source changes not appearing:** reload the browser and restart the local server if necessary.
- **Do not open the HTML file directly from disk** when testing the server. Use the localhost URL because the app fetches its knowledge JSON.

## Option C: Add optional local AI

Install Ollama separately and ensure it is running on your computer. The app remains usable without it.

~~~powershell
ollama pull llama3.2:3b
$env:HELPDESK_USE_OLLAMA = "1"
$env:HELPDESK_MODEL = "llama3.2:3b"
python projects/ai-helpdesk-copilot/server.py
~~~

When it returns generated text, the result is labeled **LOCAL AI · REVIEW OUTPUT**. If Ollama fails to respond, the system falls back to the source-backed checklist.

**Important:** The website never downloads a model itself. A local Ollama model requires its own installation and disk/RAM resources. The model is not hosted by GitHub Pages.

## Test commands

~~~powershell
python -m unittest discover -s projects/ai-helpdesk-copilot/tests -v
python scripts/check_site.py
~~~

## What should I show a recruiter?

1. Start with the public live demo.
2. Ask a realistic but fictional support question.
3. Point to the exact cited article and the reasoning checklist.
4. Show practice ticket creation and closure.
5. Explain the difference between the static demonstration and the local Python + SQLite version.
6. Describe validation and the limits of generated AI guidance.
