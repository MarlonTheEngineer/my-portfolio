/* Release Control Room: real public GitHub Actions status + clearly labeled teaching simulator.
   No authentication tokens, backend service, or external UI dependencies. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const API = "https://api.github.com/repos/MarlonTheEngineer/my-portfolio/actions/runs?per_page=75";
  const ACTIONS_URL = "https://github.com/MarlonTheEngineer/my-portfolio/actions";
  const CONFIG = [
    {key: "ci", predicate: r => r.name === "Portfolio CI / Release Pipeline" || r.name === "Portfolio quality checks", fallback: ACTIONS_URL},
    {key: "deploy", predicate: r => /pages build and deployment/i.test(r.name), fallback: "https://github.com/MarlonTheEngineer/my-portfolio/deployments"},
    {key: "smoke", predicate: r => r.name === "Portfolio Post-Deploy Smoke", fallback: ACTIONS_URL},
  ];
  const scenarios = {
    clean: {
      steps: ["pass", "pass", "pass", "pass", "pass"], verdict: "SUCCESS",
      title: "All checks passed",
      detail: "The tests pass, the reproducible ZIP verifies, GitHub Pages publishes from main/docs, and public routes respond correctly. This is an illustrative run, not a workflow execution."
    },
    link: {
      steps: ["pass", "fail", "skip", "skip", "skip"], verdict: "QUALITY FAILURE",
      title: "The missing link is detected",
      detail: "The custom HTML auditor finds missing.html. CI refuses to create the verified release ZIP. Important: branch-based GitHub Pages is independent and might still publish this main-branch change; switch to a gated Actions deployment for strict blocking."
    },
    unit: {
      steps: ["pass", "fail", "skip", "skip", "skip"], verdict: "TEST FAILURE",
      title: "A regression breaks the test suite",
      detail: "The Python test job exits nonzero on a failing assertion. The release ZIP job is skipped. Branch-based GitHub Pages is currently separate and does not automatically wait for these tests."
    },
    tamper: {
      steps: ["pass", "pass", "fail", "skip", "skip"], verdict: "INTEGRITY FAILURE",
      title: "A checksum doesn't match",
      detail: "Release verification recomputes SHA-256 from each archived file. A changed file no longer matches the manifest, so artifact verification fails. This protects the CI package, not the independent Pages branch."
    },
    live: {
      steps: ["pass", "pass", "pass", "pass", "fail"], verdict: "DEPLOYMENT ALERT",
      title: "Smoke test caught a broken public page",
      detail: "The post-deploy checker requests the published page over HTTPS and sees an error or unexpected content. The monitoring job fails visibly in GitHub Actions so the issue can be investigated."
    }
  };

  function stateTag(run) {
    if (!run) return {label:"NOT FOUND",cls:"unavailable"};
    if (run.status !== "completed") return {label:"RUNNING",cls:"pending"};
    if (run.conclusion === "success") return {label:"PASSED",cls:"success"};
    if (run.conclusion === "skipped" || run.conclusion === "cancelled") return {label:run.conclusion.toUpperCase(),cls:"unavailable"};
    return {label:"FAILED",cls:"failure"};
  }
  function updateRun(config, run) {
    const key = config.key;
    const badge = $(key + "-state");
    const state = stateTag(run);
    badge.className = "state " + state.cls;
    badge.textContent = state.label;
    $(key + "-title").textContent = run ? (run.display_title || run.name || "Workflow run") : "No recent run found";
    $(key + "-subtitle").textContent = run
      ? "Run #" + run.run_number + " · " + new Date(run.created_at).toLocaleString() + " · " + (run.head_branch || "main")
      : "View GitHub Actions for the full execution history.";
    const link = $(key + "-link");
    link.href = run && /^https:\/\/github\.com\/MarlonTheEngineer\/my-portfolio\/actions\/runs\/[0-9]+$/.test(run.html_url)
      ? run.html_url : config.fallback;
  }
  async function refresh() {
    $("refresh").disabled = true;
    $("api-message").textContent = "Checking public GitHub Actions run history...";
    try {
      const response = await fetch(API, {headers: {"Accept": "application/vnd.github+json"}, cache:"no-store"});
      if (!response.ok) throw new Error("GitHub API HTTP " + response.status);
      const payload = await response.json();
      if (!Array.isArray(payload.workflow_runs)) throw new Error("Unexpected API response");
      const runs = payload.workflow_runs.filter(r => r.head_branch === "main").sort((a,b) => new Date(b.created_at)-new Date(a.created_at));
      CONFIG.forEach(config => updateRun(config, runs.find(config.predicate)));
      $("api-message").textContent = "Showing public runs from the GitHub API. This site does not store credentials or modify deployments.";
    } catch (error) {
      CONFIG.forEach(config => updateRun(config, null));
      $("api-message").textContent = "Live status temporarily unavailable (" + error.message + "). Open the workflow links to view authoritative run results.";
    } finally {
      $("refresh").disabled = false;
    }
  }
  function simulate() {
    const result = scenarios[$("scenario").value];
    if (!result) return;
    document.querySelectorAll("[data-step]").forEach((el, index) => {
      el.className = "segment " + result.steps[index];
    });
    $("simulation-badge").textContent = result.verdict;
    $("simulation-badge").style.color = result.steps.includes("fail") ? "#ff9da7" : "#65e5bd";
    $("simulation-headline").textContent = result.title;
    $("simulation-result").textContent = result.detail;
  }
  $("refresh").addEventListener("click", refresh);
  $("simulate").addEventListener("click", simulate);
  refresh();
})();
