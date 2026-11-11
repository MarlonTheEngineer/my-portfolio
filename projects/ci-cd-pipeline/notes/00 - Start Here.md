---
tags: [devops, ci-cd, software-engineering, portfolio]
---
# My Automated Testing and Deployment Pipeline

> [!summary] My simple explanation
> I built an automation system for my GitHub portfolio. When I push changes, GitHub runs tests and checks the website. If the code passes, it creates a ZIP of the website with SHA-256 checksums. GitHub Pages independently publishes my main/docs folder, and another workflow checks that the public pages load.

**[Live Release Control Room](https://marlontheengineer.github.io/my-portfolio/pipeline/)** | **[Project source](https://github.com/MarlonTheEngineer/my-portfolio/tree/main/projects/ci-cd-pipeline)**

## What CI/CD means

- **CI, Continuous Integration:** Run automated tests whenever code changes.
- **CD, Continuous Delivery/Deployment:** Package software and move it toward users through repeatable steps.
- **Workflow:** A YAML file describing jobs GitHub should run.
- **Artifact:** A stored output from a build, like a ZIP.
- **SHA-256 hash:** A file fingerprint that detects changes.
- **Smoke test:** A quick check that important public pages actually work.

## Follow the lessons

1. [[01 - How We Built It]]
2. [[02 - How To Run It]]
3. [[03 - Understanding Deployment Safety]]

## Actual project flow

~~~mermaid
flowchart TD
 A["Push code"] --> B["Run automated tests"]
 B -->|"pass"| C["Create ZIP + SHA-256 file manifest"]
 C --> D["Verify ZIP and upload artifact"]
 B -->|"fail"| E["Mark pipeline failed"]
 A --> F["GitHub Pages publishes main/docs"]
 F --> G["Post-deployment page checks"]
~~~

> [!warning] Important detail
> Our current Pages setup publishes from a branch, independently of CI. A CI failure prevents the verified ZIP artifact, **not** the Pages publication. Strict blocking deployment would require Actions-based Pages publishing and branch protection. The web demo explains this honestly.

## One exercise to start

Open GitHub Actions, select the **Portfolio CI / Release Pipeline** workflow, and inspect the most recent run. Try to explain why the pipeline has both a testing stage and a packaging stage.
