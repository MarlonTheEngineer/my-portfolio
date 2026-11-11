---
tags: [devops, security, release-engineering]
---
# Understanding Deployment Safety and Limits

Return to [[00 - Start Here]]

## Why passing tests is useful

Automated tests repeatedly check code instead of depending on me to remember every step.

A failed unit test indicates a specific regression; a failed link audit catches a broken website reference; a changed ZIP causes a SHA-256 mismatch.

## What SHA-256 really proves

The release manifest stores a checksum for each file. When I run verify, the program calculates a new checksum and compares it to the stored value.

~~~mermaid
flowchart TD
 A["Archived file bytes"] --> B["Calculate SHA-256"]
 B --> C{"Matches stored hash?"}
 C -->|"yes"| D["File integrity accepted"]
 C -->|"no"| E["Release rejected"]
~~~

A checksum proves consistency with the manifest; it **does not prove identity** or replace digital signatures.

## Three separate things

**Tests:** tell us whether specific code behaviors passed.

**Build artifact:** an inspectable ZIP whose contents match its checksums.

**Production deployment:** the actual website published by GitHub Pages.

Right now, the first two are connected by a quality gate, while GitHub Pages publishes directly from main/docs regardless of the independent test result. That is why our site includes a prominent deployment architecture warning.

## Future improvements

- Require passing CI checks before merging to main.
- Switch GitHub Pages source to GitHub Actions.
- Add a deploy-pages job that depends on successful validation.
- Add supply-chain signing/attestation if the project needs stronger provenance.
- Add automated rollback or release approval for higher-stakes systems.

**My takeaway:** I should never describe a pipeline as blocking production unless the actual production deployment requires passing that pipeline.
