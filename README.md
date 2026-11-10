# Marlon Taylor | Technical Portfolio
This repository contains a new static portfolio website and practical Python learning projects.

## Website
Site files: `docs/index.html` and `docs/styles.css`. Open `docs/index.html` locally to preview.

To publish on GitHub Pages: visit **Settings > Pages**, select **Deploy from a branch**, then select **main** and **/docs**. Once GitHub confirms the build, use the Pages URL shown in Settings.

## Git quick start (PowerShell)
1. Install Git: https://git-scm.com/download/win
2. Run `git --version`.
3. Configure `git config --global user.name "Marlon Taylor"` and `git config --global user.email "YOUR_GITHUB_EMAIL"`.
4. Clone with `git clone https://github.com/MarlonTheEngineer/my-portfolio.git`.
5. Run `cd my-portfolio` and `git status`.
6. Create a branch: `git switch -c feature/update-portfolio`.
7. Edit the headline in `docs/index.html`.
8. Review with `git diff`, stage with `git add docs/index.html`, then commit with `git commit -m "Update portfolio introduction"`.
9. Upload the branch with `git push -u origin feature/update-portfolio`.
10. On GitHub, open a pull request and merge it after reviewing the changes.

Do not upload account credentials, tokens, production logs, or customer data.

## Projects
- [Helpdesk Ticket Tracker](projects/helpdesk-ticket-cli/README.md) (Python, SQLite)
- [Security Log Analyzer](projects/log-analyzer/README.md) (Python, structured logs)

The previous Create React App scaffolding remains in the root, but the static site in docs does not require React or npm.
