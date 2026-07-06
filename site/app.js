// ---- Configure this for your repo ----
const OWNER = "eddbr";
const REPO = "llm-safety-evals";
const BRANCH = "main";
// ---------------------------------------

const LEADERBOARD_URL = `https://raw.githubusercontent.com/${OWNER}/${REPO}/${BRANCH}/results/leaderboard.json`;
const REPO_URL = `https://github.com/${OWNER}/${REPO}`;
const TRANSCRIPT_BASE = `https://github.com/${OWNER}/${REPO}/blob/${BRANCH}/results/`;

document.getElementById("repo-link").href = REPO_URL;

let allRuns = [];
let sortKey = "attack_success_rate";
let sortDir = "desc";

function asrColor(rate) {
  // interpolate between safe (low ASR) and danger (high ASR)
  const safe = [90, 156, 120];
  const danger = [209, 86, 76];
  const t = Math.max(0, Math.min(1, rate));
  const rgb = safe.map((c, i) => Math.round(c + (danger[i] - c) * t));
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}

function renderStats(runs) {
  const models = new Set(runs.map((r) => r.model_id)).size;
  const evals = new Set(runs.map((r) => r.eval)).size;
  const totalPrompts = runs.reduce((sum, r) => sum + r.n_prompts, 0);

  const statsRow = document.getElementById("stats-row");
  statsRow.innerHTML = "";
  const stats = [
    { label: "models tested", value: models },
    { label: "benchmarks", value: evals },
    { label: "runs logged", value: runs.length },
    { label: "prompts total", value: totalPrompts.toLocaleString() },
  ];
  for (const s of stats) {
    const div = document.createElement("div");
    div.className = "stat";
    div.innerHTML = `<span class="stat-value">${s.value}</span><span class="stat-label">${s.label}</span>`;
    statsRow.appendChild(div);
  }
}

function renderTable(runs) {
  const tbody = document.getElementById("ledger-body");
  tbody.innerHTML = "";

  if (runs.length === 0) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="6">no matching runs.</td></tr>`;
    return;
  }

  for (const r of runs) {
    const tr = document.createElement("tr");
    const pct = Math.round(r.attack_success_rate * 100);
    const color = asrColor(r.attack_success_rate);

    tr.innerHTML = `
      <td class="model-cell">${r.model_id}</td>
      <td class="eval-cell">${r.eval}</td>
      <td class="scorer-cell">${r.scorer}</td>
      <td class="num">${r.n_prompts}</td>
      <td class="asr-cell">
        <div class="asr-meter">
          <div class="asr-fill" style="width:${pct}%; background:${color}22; border-left: 2px solid ${color};"></div>
          <div class="asr-label" style="color:${color};">${pct}%</div>
        </div>
      </td>
      <td class="transcript-col">
        <a class="transcript-link" href="${TRANSCRIPT_BASE}${encodeURIComponent(r.transcript_file)}" target="_blank" rel="noopener">transcript →</a>
      </td>
    `;
    tbody.appendChild(tr);
  }
}

function applySortAndFilter() {
  const query = document.getElementById("search").value.trim().toLowerCase();
  let rows = allRuns.filter(
    (r) =>
      !query ||
      r.model_id.toLowerCase().includes(query) ||
      r.eval.toLowerCase().includes(query)
  );

  rows.sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    const cmp = typeof av === "string" ? av.localeCompare(bv) : av - bv;
    return sortDir === "asc" ? cmp : -cmp;
  });

  renderTable(rows);
}

function setupSortHeaders() {
  document.querySelectorAll(".ledger thead th[data-key]").forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.key;
      if (sortKey === key) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
      } else {
        sortKey = key;
        sortDir = "desc";
      }
      document
        .querySelectorAll(".ledger thead th[data-key]")
        .forEach((h) => h.removeAttribute("aria-sort"));
      th.setAttribute("aria-sort", sortDir === "asc" ? "ascending" : "descending");
      applySortAndFilter();
    });
  });
}

async function load() {
  setupSortHeaders();
  document.getElementById("search").addEventListener("input", applySortAndFilter);

  try {
    const res = await fetch(LEADERBOARD_URL, { cache: "no-store" });
    if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
    const data = await res.json();

    allRuns = data.runs || [];
    document.getElementById("last-updated").textContent = data.generated_at_utc
      ? `updated ${new Date(data.generated_at_utc).toLocaleString()}`
      : "";

    if (allRuns.length === 0) {
      document.getElementById("ledger-body").innerHTML =
        `<tr class="empty-row"><td colspan="6">no runs logged yet. push results from the Colab notebook to populate this page.</td></tr>`;
      return;
    }

    renderStats(allRuns);
    applySortAndFilter();
  } catch (err) {
    document.getElementById("ledger-body").innerHTML =
      `<tr class="empty-row"><td colspan="6">couldn't read the ledger (${err.message}). check that OWNER/REPO in app.js point at your repo, and that results/leaderboard.json exists there.</td></tr>`;
  }
}

load();
