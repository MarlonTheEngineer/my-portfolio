/* AI Helpdesk Copilot frontend. Works on GitHub Pages with no backend.
 * On http://127.0.0.1:8000 it additionally talks to the optional local Python API.
 * For educational examples only. Never enter real client or credential information. */
(() => {
  "use strict";

  const $ = id => document.getElementById(id);
  const STOP = new Set("a an and are be can do does for from how i in is it my of on or the this to we what when with you please help issue problem not will why work working user users".split(" "));
  const DEMO_TICKETS = [
    { id: "D-101", title: "Sample VPN connectivity issue", description: "Synthetic example, no customer information", category: "Networking", priority: "medium", status: "open", created_at: "" },
    { id: "D-102", title: "Sample printer queue issue", description: "Synthetic example, no customer information", category: "Hardware", priority: "low", status: "closed", created_at: "" }
  ];
  let articles = [];
  let tickets = [...DEMO_TICKETS];
  let backend = false;
  let localAI = false;
  let asks = 0;

  const tokenize = s => new Set((String(s).toLowerCase().match(/[a-z0-9]+/g) || []).filter(w => !STOP.has(w)));
  const matched = (query, max = 3) => {
    const input = tokenize(query);
    return articles.map(article => {
      const title = tokenize(article.title);
      const keywords = tokenize(article.keywords.join(" "));
      const body = tokenize(article.summary + " " + article.steps.join(" "));
      let score = 0;
      for (const word of input) {
        if (title.has(word)) score += 4;
        if (keywords.has(word)) score += 3;
        if (body.has(word)) score += 1;
      }
      return { article, score };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score || a.article.id.localeCompare(b.article.id)).slice(0, max).map(x => x.article);
  };

  const guided = hits => {
    if (!hits.length) return "I couldn't find a matching runbook. Record the exact symptoms and error message, follow approved troubleshooting procedures, and escalate if needed. I don't have a source-backed fix for this question.";
    const a = hits[0];
    const lines = [a.summary, "", "Suggested checklist [" + a.id + "]:"];
    a.steps.forEach((step, i) => lines.push((i + 1) + ". " + step));
    lines.push("", "Safety note: " + a.caution);
    return lines.join("\n");
  };

  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = String(text);
    return el;
  }
  function addMessage(role, text, mode) {
    const log = $("messages");
    const message = node("div", "message " + role);
    message.append(node("span", "speaker", role === "user" ? "YOUR QUESTION" : (mode === "local-ai" ? "LOCAL AI · REVIEW OUTPUT" : "KNOWLEDGE-GUIDED RESPONSE")));
    message.append(node("p", "", text));
    log.append(message);
    while (log.children.length > 13) log.children[1].remove();
    log.scrollTop = log.scrollHeight;
  }
  function renderSources(hits) {
    const box = $("sources");
    box.replaceChildren();
    if (!hits.length) {
      const empty = node("div", "empty");
      empty.append(node("span", "empty-icon", "⌕"), node("p", "", "No matching article found. Try another specific symptom."));
      box.append(empty); return;
    }
    hits.forEach((a, i) => {
      const card = node("article", "source");
      const head = node("div", "source-head");
      head.append(node("span", "source-code", a.id), node("span", "source-cat", i === 0 ? "BEST MATCH" : "RELATED"));
      card.append(head, node("h3", "", a.title), node("p", "", a.summary));
      const detail = node("details", "");
      const summary = node("summary", "", "Read troubleshooting steps");
      const list = node("ol", "");
      a.steps.forEach(step => list.append(node("li", "", step)));
      detail.append(summary, list, node("p", "caution", "Safety: " + a.caution));
      card.append(detail);
      box.append(card);
    });
  }
  function renderArticles(filter = "") {
    const box = $("kb-list");
    box.replaceChildren();
    const query = filter.trim().toLowerCase();
    const shown = articles.filter(a => !query || (a.title + " " + a.summary + " " + a.category + " " + a.keywords.join(" ")).toLowerCase().includes(query));
    $("kb-count").textContent = shown.length + " results";
    if (!shown.length) box.append(node("p", "hint", "No matching article. Try another search."));
    shown.forEach(a => {
      const card = node("article", "kb-card");
      card.id = "article-" + a.id;
      card.append(node("span", "source-code", a.id + " / " + a.category), node("h3", "", a.title), node("p", "", a.summary));
      const details = node("details", "");
      const ol = node("ol", "");
      a.steps.forEach(step => ol.append(node("li", "", step)));
      details.append(node("summary", "", "Read the full checklist"), ol, node("p", "caution", "Safety: " + a.caution));
      card.append(details);
      box.append(card);
    });
  }
  function renderTickets() {
    const list = $("ticket-list");
    list.replaceChildren();
    $("ticket-count").textContent = tickets.length;
    $("open-count").textContent = tickets.filter(t => t.status === "open").length;
    $("queue-status").textContent = backend ? "SQLite · local server" : "In-memory practice queue";
    if (!tickets.length) list.append(node("p", "hint", "No tickets yet. Create a fictional example."));
    tickets.slice(0, 50).forEach(t => {
      const row = node("article", "ticket");
      const detail = node("div", "");
      detail.append(node("span", "ticket-id", "#" + t.id + " · " + t.category), node("h4", "", t.title), node("p", "", t.priority.toUpperCase() + " PRIORITY · " + (t.description || "No additional details")));
      const actions = node("div", "ticket-actions");
      actions.append(node("span", "tag " + t.status, t.status.toUpperCase()));
      if (t.status === "open") {
        const close = node("button", "", "Close");
        close.type = "button";
        close.setAttribute("aria-label", "Close ticket " + t.id);
        close.addEventListener("click", async () => {
          close.disabled = true;
          if (backend) {
            try {
              const response = await fetch("/api/tickets/" + encodeURIComponent(t.id) + "/close", { method: "POST", headers: {"Content-Type":"application/json"}, body:"{}" });
              if (!response.ok) throw Error("Could not close ticket");
            } catch {
              $("ticket-info").textContent = "Could not close the ticket. Check your local server.";
              close.disabled = false; return;
            }
          }
          t.status = "closed";
          renderTickets();
        });
        actions.append(close);
      }
      row.append(detail, actions);
      list.append(row);
    });
  }
  async function ask(question) {
    if (!articles.length) {
      addMessage("assistant", "Knowledge base is unavailable. Reload the page and try again.", "knowledge");
      return;
    }
    addMessage("user", question);
    $("ask-button").disabled = true;
    $("ask-button").textContent = "Searching...";
    let result;
    try {
      if (backend) {
        const response = await fetch("/api/assist", {
          method: "POST", headers: {"Content-Type": "application/json"},
          body: JSON.stringify({question})
        });
        if (!response.ok) throw Error("Local service returned " + response.status);
        result = await response.json();
      } else {
        const hits = matched(question);
        result = { mode: "knowledge", answer: guided(hits), sources: hits };
      }
    } catch {
      const hits = matched(question);
      result = {mode:"knowledge",answer:guided(hits) + "\n\n(Local API unavailable; shown from browser knowledge base.)",sources:hits};
    } finally {
      $("ask-button").disabled = false;
      $("ask-button").textContent = "Find guidance ↗";
    }
    addMessage("assistant", result.answer, result.mode);
    renderSources(result.sources || []);
    asks += 1;
  }
  async function createTicket(event) {
    event.preventDefault();
    const title = $("ticket-title").value.trim();
    const description = $("ticket-description").value.trim();
    if (title.length < 3 || title.length > 120 || description.length > 1200) return;
    const payload = {title,description,category:$("ticket-category").value,priority:$("ticket-priority").value};
    const button = $("ticket-button");
    button.disabled = true;
    try {
      if (backend) {
        const response = await fetch("/api/tickets", {
          method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw Error(data.error || "Ticket creation failed");
        tickets.unshift(data.ticket);
        $("ticket-info").textContent = "Saved ticket #" + data.ticket.id + " to local SQLite.";
      } else {
        tickets.unshift({ ...payload, id: "D-" + (100 + tickets.length + 1), status: "open", created_at: "" });
        $("ticket-info").textContent = "Practice ticket created in browser memory. It will disappear on refresh.";
      }
      $("ticket-form").reset();
      renderTickets();
    } catch (error) {
      $("ticket-info").textContent = "Could not create ticket: " + error.message;
    } finally {button.disabled = false;}
  }
  async function init() {
    try {
      const response = await fetch("knowledge.json", {cache:"no-store"});
      if (!response.ok) throw Error("Could not load knowledge articles");
      const kb = await response.json();
      articles = kb.articles;
      $("article-count").textContent = articles.length;
      renderArticles();
    } catch {
      $("mode-label").textContent = "Knowledge file unavailable";
      $("kb-list").append(node("p", "", "Could not load the knowledge base."));
      return;
    }
    const localHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
    if (localHost) {
      try {
        const response = await fetch("/api/health", {cache:"no-store"});
        if (response.ok) {
          const info = await response.json();
          backend = info.server === "local";
          localAI = info.ollama_enabled === true;
        }
        if (backend) {
          const responseTickets = await fetch("/api/tickets", {cache:"no-store"});
          if (responseTickets.ok) tickets = (await responseTickets.json()).tickets;
        }
      } catch {backend = false;}
    }
    $("mode-label").textContent = backend ? (localAI ? "Local AI enabled · Ollama optional" : "Local server · sourced guidance") : "Public demo · sourced guidance";
    $("storage-label").textContent = backend ? "LOCAL SQLITE STORAGE" : "BROWSER-ONLY SAMPLES";
    renderTickets();
  }
  $("assist-form").addEventListener("submit", event => {
    event.preventDefault();
    const question = $("question").value.trim();
    if (question.length < 3 || question.length > 600) return;
    $("question").value = "";
    ask(question);
  });
  document.querySelectorAll("[data-ask]").forEach(button => button.addEventListener("click", () => {
    $("question").value = button.dataset.ask;
    $("assist-form").requestSubmit();
  }));
  $("ticket-form").addEventListener("submit", createTicket);
  $("kb-search").addEventListener("input", event => renderArticles(event.target.value));
  init();
})();
