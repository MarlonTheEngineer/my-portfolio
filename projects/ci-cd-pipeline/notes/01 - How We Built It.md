---
tags: [devops, python, github-actions, walkthrough]
---
# How We Built the CI/CD Pipeline

Return to [[00 - Start Here]] | Next: [[02 - How To Run It]]

## Step 1: Reuse the real portfolio

The existing GitHub repository already hosts Python projects, JavaScript demos, and the website under docs/. The goal was to **automate checking and releasing those real files**, not create an empty workflow diagram.

## Step 2: Build a Python release tool

We created projects/ci-cd-pipeline/pipeline.py with four CLI commands:

| Command | What it does |
| --- | --- |
| check | Parse each HTML page and inspect local links and assets |
| build | Create a deterministic ZIP and file manifest |
| verify | Recompute checksums and detect archive tampering |
| smoke | Request important live web pages and validate responses |

Each command returns a nonzero exit status when validation fails. GitHub Actions can detect that and mark the step failed.

## Step 3: Test the tests

The tests/test_pipeline.py file creates temporary websites and runs the release functions. We intentionally break a link, remove a page anchor, modify a ZIP after packaging, and insert an unexpected archive file.

**Why?** To show that errors are caught, not merely that good inputs pass.

## Step 4: Add GitHub Actions

The .github/workflows/python-tests.yml workflow runs a matrix with Python 3.11 and 3.12, plus Node.js 22.

The main pattern is:

~~~mermaid
flowchart LR
 A["Validate 3.11"] --> C["Release job"]
 B["Validate 3.12"] --> C
 C --> D["Verified artifact"]
~~~

The release job uses **needs: validate**, which means it starts only after validation succeeds.

## Step 5: Preserve free deployment

The repository already uses GitHub Pages set to main/docs. We left it alone so the website stays free and functional.

The workflow still builds a release archive as a separate, inspectable output. See [[03 - Understanding Deployment Safety]] for why this is not yet a strict publication gate.

## Step 6: Add checks after publishing

The post-deploy-smoke.yml workflow requests the portfolio homepage, neural-network page, helpdesk-copilot page, and Release Control Room via HTTPS. It requires HTTP success and expected content.

It can run after a successful Pages build where GitHub emits the matching workflow event, on demand, and weekly.

## Step 7: Make the portfolio page useful

The docs/pipeline/ page shows actual GitHub Actions statuses using public API data and includes a **separate labeled simulation** that teaches how breakages affect stages.

## My takeaway

**CI/CD is not just a "deploy" button.** It is a chain of measurable checks and repeatable actions with clear failure signals.
