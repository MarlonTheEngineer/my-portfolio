---
tags: [practice, software-engineering, ai, learning]
---
# My Practice Exercises

Return to [[00 - Start Here]] | Previous: [[05 - Security and Testing]]

> [!tip] Rule for practice
> Change one small thing at a time, predict the result, run tests, and explain what happened in my own words.

## Experiment 1: Understand the search ranking

- [ ] Search for "account locked".
- [ ] Search for "VPN connection".
- [ ] Search for a nonsense phrase.
- [ ] Explain why the third search should report no reliable source.

**My explanation:** 

## Experiment 2: Add a new knowledge article

- [ ] Open docs/helpdesk-copilot/knowledge.json.
- [ ] Create a new article with a unique KB ID.
- [ ] Add a title, keywords, description, safe troubleshooting steps, and caution.
- [ ] Reload the web page and check whether it appears in the article catalog.
- [ ] Create a test that matches it.

**What changed:** 

## Experiment 3: Test tickets

- [ ] Create a fictional high-priority ticket.
- [ ] Close it.
- [ ] Refresh in public mode. What happens?
- [ ] Start the local Python server and try again. What changes?

**My explanation of SQLite:** 

## Experiment 4: Read a Python route

Find the POST /api/tickets branch in server.py.

- [ ] Describe what JSON request the browser sends.
- [ ] Identify the validation code.
- [ ] Locate the SQLite INSERT.
- [ ] Find the JSON response.

**My description:** 

## Experiment 5: Run tests, then deliberately break one

- [ ] Run the Python tests.
- [ ] Temporarily change one article ID in a local copy.
- [ ] Observe which test fails and why.
- [ ] Restore the code and run tests again.

**What I learned:** 

## Experiment 6: Optional Ollama

- [ ] Explain the difference between a retrieved checklist and a generated answer.
- [ ] Enable local Ollama, if installed.
- [ ] Ask a fictional supported question.
- [ ] Check whether the answer is actually backed by the source.
- [ ] Ask something outside the runbooks. How does the model respond?

**Warning:** A local model may still hallucinate even when given references.

## Explain the project in 30 seconds

> I made an educational Helpdesk Copilot that searches troubleshooting articles and shows evidence for its recommendations. The public version runs on GitHub Pages with JavaScript. The local version uses Python and SQLite to keep practice tickets, and it can optionally use Ollama for language-model responses. I built it to demonstrate full-stack development, retrieval, testing, and safe support workflows.

Adapt this script into **my own words** after trying the features and reading the code.
