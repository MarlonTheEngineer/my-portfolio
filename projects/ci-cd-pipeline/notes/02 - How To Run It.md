---
tags: [devops, windows, runbook, testing]
---
# How I Run and Operate My Pipeline

Return to [[00 - Start Here]] | Next: [[03 - Understanding Deployment Safety]]

## Open the live dashboard

https://marlontheengineer.github.io/my-portfolio/pipeline/

The three status cards query **real** GitHub Actions runs. The failure lab is a **simulation** and does not touch the repository.

## Run the Python tools on Windows

From PowerShell:

~~~powershell
git clone https://github.com/MarlonTheEngineer/my-portfolio.git
cd my-portfolio

python projects/ci-cd-pipeline/pipeline.py check
python projects/ci-cd-pipeline/pipeline.py build --output dist/portfolio-release.zip
python projects/ci-cd-pipeline/pipeline.py verify dist/portfolio-release.zip
python -m unittest discover -s projects/ci-cd-pipeline/tests -v
~~~

The ZIP under dist/ is a release artifact. It contains the website plus a RELEASE-MANIFEST.json file listing SHA-256 hashes.

## Check the real published website

~~~powershell
python projects/ci-cd-pipeline/pipeline.py smoke
~~~

This uses the network. It fails if a required page does not load or lacks the expected content.

## View CI in GitHub

1. Open https://github.com/MarlonTheEngineer/my-portfolio/actions
2. Select **Portfolio CI / Release Pipeline**.
3. Open the latest run.
4. Examine the Python 3.11 and 3.12 jobs.
5. Inspect the release packaging job and download the ZIP artifact if available.

## Safe testing procedure

- [ ] Create a feature branch.
- [ ] Intentionally change a local page to link to missing.html.
- [ ] Push the branch or open a pull request.
- [ ] Observe the audit failure in GitHub Actions.
- [ ] Fix the link.
- [ ] Re-run and confirm success.
- [ ] Never commit an intentional failure directly to main.

## How to stop an error from spreading

Review CI failures before merging and consider requiring passing checks in GitHub branch protection. Current Pages still deploys main/docs separately, so branch protection helps prevent broken main commits. A strict gated deployment requires additional changes to Pages settings.
