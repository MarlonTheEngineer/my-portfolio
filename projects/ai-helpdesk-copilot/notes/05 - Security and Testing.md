---
tags: [security, testing, ai-safety, devops]
---
# Security, Testing, and Honest Limits

Return to [[00 - Start Here]] | Previous: [[04 - The Code Explained]]

## Why this is a learning tool, not production helpdesk software

A real IT helpdesk deals with personal information, account permissions, and sometimes sensitive security incidents. My current app is a demonstration of concepts, not a security-approved enterprise system.

**Never enter real passwords, customer records, private logs, or secret tokens.**

## Defensive choices in this version

- The Python server listens on 127.0.0.1 only.
- It checks same-origin requests and accepts limited JSON body sizes.
- Ticket inputs have limits and approved category/priority values.
- SQLite operations use parameterized queries.
- The browser displays user input as text rather than interpreting it as HTML.
- Knowledge articles include cautions against bypassing MFA or organizational policies.
- The AI endpoint, when enabled, points to localhost:11434, not a hosted provider.
- No secrets or production logs should be included in the repository.

## What is still missing

- Login and proper multiuser authentication
- Role-based access control
- Sensitive-data redaction and retention controls
- Rate limiting and formal threat modeling
- Hardened deployment, monitoring, and audit logs
- A verified evaluation set for answer quality and hallucinations
- Reliable protection against all prompt-injection attempts

These missing features are reasons **not to expose the local server to a network**.

## Tests and what they prove

Run:

~~~powershell
python -m unittest discover -s projects/ai-helpdesk-copilot/tests -v
~~~

Expected topics:

| Test | Why it matters |
|---|---|
| Catalog contains unique source IDs | Prevent confusing citations |
| Locked account question matches KB-001 | Checks a high-value retrieval case |
| Phishing question matches KB-010 | Checks another category |
| Unrelated question returns no match | Discourages unsupported advice |
| Ticket validation rejects invalid input | Avoids corrupt stored data |
| SQL-looking ticket title remains data | Demonstrates parameterized SQL |
| Local API routes respond | Tests integration, not just isolated functions |
| Cross-origin request rejected | Shows an important local boundary |

**A passing test suite is evidence of covered behavior, not proof of total security.**

## How to review AI answers responsibly

Before acting on advice, I should ask:

1. Is there a cited KB article?
2. Does the cited article actually support this step?
3. Do I have authorization to perform it?
4. Could this risk access, confidentiality, or availability?
5. Should I escalate instead?

## Production roadmap

A responsible next iteration could add authenticated users, role permissions, source versioning, redacted audit logs, known-question evaluations, and human review. A hosted backend would need a separate security and cost plan.

## My takeaway

**Good software engineering means describing what works and exactly where the safety boundaries are.**
