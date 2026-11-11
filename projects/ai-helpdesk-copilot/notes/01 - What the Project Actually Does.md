---
tags: [helpdesk, ai, fundamentals]
---
# What the Project Actually Does

Return to [[00 - Start Here]].

## My explanation to someone else

Imagine a support technician gets a message: "I can't log into my computer."

Instead of guessing, my Helpdesk Copilot searches a collection of troubleshooting guides. It selects the most relevant guide and lists the recommended checks, including a source ID such as **KB-001**.

It doesn't actually repair the computer. **It helps the technician organize the investigation.** The technician is still responsible for verification, authorization, and judgment.

## Example: a sign-in failure

~~~mermaid
flowchart TD
    A["User reports: can't sign in"] --> B["Analyze the words in the question"]
    B --> C["Find KB-001: Account locked or cannot sign in"]
    C --> D["Display checklist"]
    D --> E["Technician verifies identity and checks account state"]
    E --> F["Create and update a practice ticket"]
~~~

## Four main capabilities

**1. Troubleshooting search**

It looks for matching words in article titles, keywords, summaries, and steps.

**2. Source-backed responses**

It displays a checklist and a KB ID. You can open the full source and compare it to the answer. The system should admit when there is no good source.

**3. Ticket tracking**

A practice ticket contains a title, optional description, category, priority, and status. In the public demo it lives temporarily in memory; in the local version it is stored in SQLite.

**4. Optional local AI**

A separate Ollama language model can turn retrieved information into a natural-language explanation. This is an opt-in extra, not part of GitHub Pages hosting. Its answers can still be wrong.

## What "grounded" means

A grounded answer is connected to information we can inspect. Instead of saying "Trust me," it points to the troubleshooting article that supports its recommendation.

Grounding **reduces** unsupported claims; it does not guarantee that a language model is correct or that the article fits a real-world environment.

## How the two modes differ

| Feature | Public GitHub Pages | My laptop with local server |
|---|---|---|
| Article search | JavaScript | Python |
| Tickets | Temporary memory | SQLite file |
| Generated AI explanations | No | Optional Ollama |
| Paid cloud service needed | No | No |
| Production support safe | No | No |

## Key takeaway

**The purpose is to recommend and document troubleshooting steps, not to silently make risky changes on a user's computer.**
