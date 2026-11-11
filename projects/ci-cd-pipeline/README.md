# Automated Testing & Deployment Pipeline

**[Launch the Release Control Room](https://marlontheengineer.github.io/my-portfolio/pipeline/)** · **[Actual GitHub Actions runs](https://github.com/MarlonTheEngineer/my-portfolio/actions)** · **[Study notes](notes/00%20-%20Start%20Here.md)**

A real CI/CD portfolio project, built with Python's standard library, GitHub Actions, SHA-256 checksums, and the existing free GitHub Pages deployment.

> **Scope:** The project checks source, creates reproducible release archives, verifies integrity, monitors actual workflow runs, and probes public pages. No Vercel, npm build, paid backend, or API secrets.

## How it works

~~~mermaid
flowchart TD
    A["Push or pull request"] --> B["Quality checks on Python 3.11 and 3.12"]
    B --> C["Run Python tests, JS checks, site audit"]
    C -->|"pass"| D["Build deterministic ZIP"]
    D --> E["Verify SHA-256 manifest"]
    E --> F["Upload GitHub Actions artifact"]
    C -->|"fail"| X["Mark CI failed; artifact not created"]
    A --> G["Existing GitHub Pages branch publisher"]
    G --> H["Public website"]
    H --> I["Post-deployment HTTPS smoke checks"]
~~~

**Important architectural distinction:** GitHub Pages here publishes directly from **main → /docs**. This publisher is independent of the CI quality gate. Therefore, **a failed test does not prevent a commit on main from becoming public**. CI controls the verified release ZIP, not the Pages publication. Post-deployment checks detect broken pages after publishing. A strict block-on-failure gate would require switching Pages to **GitHub Actions** deployment, adding an actions/deploy-pages job dependent on tests, and protecting main. We have deliberately preserved the working Pages configuration.

## What's automated?

| Stage | Where it runs | What it verifies |
| --- | --- | --- |
| Push / PR | GitHub | Starts the pipeline |
| Unit tests | python-tests.yml | Helpdesk CLI, log analyzer, AI copilot, release toolkit |
| Code syntax | python-tests.yml | Python compilation, Node.js syntax and neural-network tests |
| Site audit | pipeline.py check | All HTML pages, landmarks, links, local assets and anchors |
| Release archive | pipeline.py build | Reproducible ZIP of the static website |
| Integrity | pipeline.py verify | File sizes, SHA-256, no unexpected members |
| Publication | Native GitHub Pages | Serves main/docs |
| Public URL health | post-deploy-smoke.yml | Checks four public routes over HTTPS |
| Run dashboard | docs/pipeline/app.js | Read-only GitHub Actions status with fallback links |

The release ZIP is a GitHub Actions artifact for **7 days**. The GitHub Pages publisher currently serves the tracked docs folder, not the ZIP.

## Run it locally

Requires Python 3.10+ and Node.js for the JavaScript test. Run from a cloned repository:

~~~powershell
git clone https://github.com/MarlonTheEngineer/my-portfolio.git
cd my-portfolio

# Check every page and its local resources
python projects/ci-cd-pipeline/pipeline.py check

# Create repeatable site ZIP plus SHA-256 manifest
python projects/ci-cd-pipeline/pipeline.py build --output dist/portfolio-release.zip

# Independently verify ZIP contents and checksums
python projects/ci-cd-pipeline/pipeline.py verify dist/portfolio-release.zip

# Run release toolkit tests
python -m unittest discover -s projects/ci-cd-pipeline/tests -v

# Check the live GitHub Pages site
python projects/ci-cd-pipeline/pipeline.py smoke
~~~

Other application tests:

~~~powershell
python -m unittest discover -s projects/helpdesk-ticket-cli/tests -v
python -m unittest discover -s projects/log-analyzer/tests -v
python -m unittest discover -s projects/ai-helpdesk-copilot/tests -v
node --test docs/neural-network/tests.js
~~~

No pip install is required. The generated ZIP is written under **dist/**, which is ignored by Git.

## How the artifact is reproducible

1. Reads regular files below docs/ and excludes symlinks.
2. Sorts files by relative path.
3. Creates RELEASE-MANIFEST.json with each file's path, SHA-256 and byte count.
4. Writes the ZIP with fixed timestamps and permissions.
5. Opens the ZIP again and independently checks every checksum.
6. Rejects missing, modified, extra, or duplicate files.

Two archives are byte-identical when they contain identical site files and use the same supplied source commit. SHA-256 is an **integrity digest**, not a signature proving the author's identity.

## Find workflow runs and download artifacts

1. Open the repository's **Actions** tab.
2. Select **Portfolio CI / Release Pipeline**.
3. Read the Python 3.11 and 3.12 testing jobs.
4. Open the **Build and verify release artifact** job.
5. Download the artifact named portfolio-site-COMMIT-SHA.
6. Use the verify command to check its ZIP.

The release control room also queries public GitHub Actions metadata from your browser. Anonymous GitHub API requests may be rate limited, so the Actions tab is authoritative.

## Safe practice exercises

Use a **feature branch**, not main, when intentionally breaking code.

### A. Broken link

Insert a link to a nonexistent file in a test branch, open a pull request, and observe the site audit fail. Restore the link and confirm tests pass.

### B. Failing unit test

Create a failing assertion in a test branch. The release artifact job will be skipped because the validation matrix failed.

### C. Tampered ZIP

Run the unit tests. One intentionally alters an archived file and verifies that SHA-256 checking rejects the package.

### D. Public health

Run the smoke command against the deployed site. Investigate failed URL or content checks rather than claiming success.

## Troubleshooting

- **Audit fails:** Fix broken relative URLs. The portfolio lives under /my-portfolio/ on GitHub Pages; root-relative links usually break.
- **No release artifact:** The package job only runs when both Python versions pass.
- **Live status unavailable:** GitHub's anonymous API can rate-limit; use the Actions page directly.
- **Smoke fails:** Inspect Pages publishing, redirects, content changes and possible propagation delay.
- **Bad main commit still published:** Branch-based Pages publishes independently of CI. See architecture limitation above.

## Project files

~~~text
.github/workflows/
  python-tests.yml              Full CI test matrix + artifact packaging
  post-deploy-smoke.yml          Public HTTPS verification
projects/ci-cd-pipeline/
  pipeline.py                    Audit, package, verify, smoke
  tests/test_pipeline.py         Unit tests, including tampering
  README.md                      Operating instructions
  notes/                         Linked Obsidian study notes
docs/pipeline/
  index.html                     Published interactive showcase
  styles.css                     Responsive status dashboard
  app.js                         Public status fetching + teaching lab
~~~

## Skills shown

Git and pull requests, CI job dependencies, testing on multiple runtimes, site audits, reproducible artifacts, SHA-256, deployment health checks, and documenting system limitations.

This is a working **DevOps and release engineering showcase**, not an enterprise-grade supply-chain attestation platform. No signed artifacts, approval gates, or automatic rollback are implemented.
