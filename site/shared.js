// Shared site config + chrome (nav / footer), injected on every page.
// Add a page here and it appears in the nav everywhere -- one edit, site-wide.

// ---- Configure this for your repo ----
const OWNER = "eddbr";
const REPO = "model-eval";
const BRANCH = "main";
// ---------------------------------------

const REPO_URL = `https://github.com/${OWNER}/${REPO}`;

// Exposed for app.js so repo config lives in exactly one place.
window.SITE_CONFIG = {
  OWNER,
  REPO,
  BRANCH,
  REPO_URL,
  LEADERBOARD_URL: `https://raw.githubusercontent.com/${OWNER}/${REPO}/${BRANCH}/results/leaderboard.json`,
  TRANSCRIPT_BASE: `https://github.com/${OWNER}/${REPO}/blob/${BRANCH}/results/`,
};

const PAGES = [
  { href: "index.html", label: "Leaderboard" },
  { href: "about.html", label: "About" },
  { href: "methodology.html", label: "How it works" },
];

function currentFile() {
  const path = location.pathname.split("/").pop();
  return path === "" ? "index.html" : path;
}

function renderNav() {
  const here = currentFile();
  const links = PAGES.map(
    (p) =>
      `<a href="${p.href}"${p.href === here ? ' class="active"' : ""}>${p.label}</a>`
  ).join("");

  const nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = `
    <div class="nav-inner">
      <a class="brand" href="index.html">
        <span class="brand-mark">S</span>
        <span class="brand-name">Open&nbsp;LLM Safety&nbsp;Index <span>/ beta</span></span>
      </a>
      <div class="nav-links">
        ${links}
        <a class="nav-repo" href="${REPO_URL}" target="_blank" rel="noopener">GitHub ↗</a>
      </div>
    </div>`;
  document.body.prepend(nav);
}

function renderFooter() {
  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML = `
    <div class="footer-inner">
      <div class="footer-col">
        <strong>Open LLM Safety Index</strong>
        <span>An independent, open safety rating for open-weight AI models.
        Every score is reproducible from public code and logged transcripts.</span>
      </div>
      <div class="footer-col">
        <a href="about.html">About &amp; mission</a>
        <a href="methodology.html">How scoring works</a>
        <a href="${REPO_URL}" target="_blank" rel="noopener">Source &amp; full pipeline on GitHub ↗</a>
      </div>
    </div>`;
  document.body.appendChild(footer);
}

renderNav();
renderFooter();
