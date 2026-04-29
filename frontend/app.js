/**
 * GeoAgent – frontend application logic.
 *
 * Communicates with the FastAPI backend (/api/agent) and renders
 * the route + geocaching clues in the UI.
 */

const API_BASE = "http://localhost:8000";

// ── DOM refs ────────────────────────────────────────────────────────────────
const cityInput     = document.getElementById("city-input");
const stopsInput    = document.getElementById("stops-input");
const stopsValue    = document.getElementById("stops-value");
const generateBtn   = document.getElementById("generate-btn");
const errorMsg      = document.getElementById("error-msg");
const resultsSection = document.getElementById("results");
const loading       = document.getElementById("loading");
const routeTitle    = document.getElementById("route-title");
const routeSummary  = document.getElementById("route-summary");
const routeNote     = document.getElementById("route-note");
const stopsContainer = document.getElementById("stops-container");
const historyList   = document.getElementById("history-list");

// ── State ───────────────────────────────────────────────────────────────────
let conversationHistory = [];

// ── UI helpers ───────────────────────────────────────────────────────────────
stopsInput.addEventListener("input", () => {
  stopsValue.textContent = stopsInput.value;
});

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove("hidden");
}

function clearError() {
  errorMsg.textContent = "";
  errorMsg.classList.add("hidden");
}

function setLoading(on) {
  loading.classList.toggle("hidden", !on);
  resultsSection.classList.add("hidden");
  generateBtn.disabled = on;
}

// ── Render ───────────────────────────────────────────────────────────────────
function renderStops(clues) {
  stopsContainer.innerHTML = "";
  clues.forEach((clue, idx) => {
    const card = document.createElement("div");
    card.className = "stop-card";
    card.innerHTML = `
      <div class="stop-number">${idx + 1}</div>
      <div class="stop-name">${escapeHtml(clue.stop_name)}</div>
      <div class="stop-coords">${clue.lat.toFixed(4)}°, ${clue.lon.toFixed(4)}°</div>
      <div class="stop-clue">${escapeHtml(clue.clue)}</div>
    `;
    stopsContainer.appendChild(card);
  });
}

function renderHistory(history) {
  historyList.innerHTML = "";
  history.forEach(({ role, content }) => {
    const div = document.createElement("div");
    div.className = `msg msg-${role === "user" ? "user" : "assistant"}`;
    div.innerHTML = `<div class="msg-role">${escapeHtml(role)}</div>${escapeHtml(content)}`;
    historyList.appendChild(div);
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Main action ──────────────────────────────────────────────────────────────
async function handleGenerate() {
  const city = cityInput.value.trim();
  const numStops = parseInt(stopsInput.value, 10);

  clearError();

  if (!city) {
    showError("Please enter a city name.");
    cityInput.focus();
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/api/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        city,
        num_stops: numStops,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${response.status}`);
    }

    const data = await response.json();
    conversationHistory = data.conversation_history;

    // Update route summary
    routeTitle.textContent = `Route: ${data.route.city}`;
    routeSummary.textContent = data.route.summary;

    if (data.route.note) {
      routeNote.textContent = data.route.note;
      routeNote.classList.remove("hidden");
    } else {
      routeNote.classList.add("hidden");
    }

    renderStops(data.clues);
    renderHistory(conversationHistory);

    setLoading(false);
    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (err) {
    setLoading(false);
    showError(err.message || "Failed to connect to the GeoAgent backend.");
  }
}

// ── Event listeners ───────────────────────────────────────────────────────────
generateBtn.addEventListener("click", handleGenerate);

cityInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleGenerate();
});
