# GeoAgent 🌍

> **An LLM-powered AI Agent for geocaching and urban exploration.**
> Multi-step reasoning · Multi-turn dialogue · FastAPI + plain JS MVP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Problem

Geocaching and urban exploration are growing hobbies, but planning a
meaningful route — one that is ordered sensibly, culturally coherent,
and enriched with engaging riddle-clues — currently requires hours of
manual research.  Existing travel apps give directions; none provide
the *adventure layer* that makes exploration genuinely fun.

## Solution

GeoAgent is an AI Agent that turns a single city name into a complete
exploration itinerary:

1. **Route Planning** — landmark selection and logical ordering
2. **Clue Generation** — cryptic geocaching riddles for each waypoint
3. **Multi-turn Dialogue** — the agent remembers prior requests and
   refines its answers across multiple turns

The agent pipeline is currently backed by a deterministic mock engine
that can be replaced with any real LLM (MiMo API, OpenAI, Anthropic)
by editing a single file (`backend/agent.py`).

---

## Agent Pipeline

```
User Input
    │
    ▼
┌───────────────────┐
│ 1. Intent Parsing │  Extract city, stop count, exploration style
└────────┬──────────┘
         │
         ▼
┌──────────────────────┐
│ 2. Route Planning    │  Select & order the best landmarks
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ 3. Clue Generation   │  Write a geocaching riddle per waypoint
└────────┬─────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. Dialogue Synthesis  │  Compose reply · append to history
└────────────────────────┘
         │
         ▼
    JSON response  (route · clues · pipeline_steps · conversation_history)
```

Every step is a self-contained function in `backend/agent.py`.
Replacing a step with a real LLM call requires no changes outside that function.

### Multi-turn Dialogue

Each `/api/agent` request accepts a `conversation_history` array.
Pass the history from the previous response back on the next call and
the agent maintains full conversational context:

```
Turn 1 → "Plan a route in London"  → history: [user, assistant]
Turn 2 → "Now show me Paris"       → history: [user, assistant, user, assistant]
Turn 3 → "Add one more stop"       → history grows with each turn
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🗺 **Route generation** | Curated, ordered landmark lists with GPS coordinates |
| 🔑 **Geocaching clues** | Riddle-style hints tied to landmark type and context |
| 🤖 **Pipeline trace** | Every API response exposes the `pipeline_steps` taken |
| 💬 **Multi-turn history** | Conversation history grows across requests |
| ⚡ **FastAPI backend** | Auto-generated OpenAPI docs at `/docs` |
| 🌐 **Zero-build frontend** | Plain HTML + CSS + JS — open `index.html` in a browser |
| 🔌 **LLM-swap ready** | Mock engine isolated in `agent.py`; no other file needs changing |

---

## Repository Structure

```
GeoAgent/
├── backend/
│   ├── main.py          # FastAPI app · four-step agent pipeline
│   ├── agent.py         # AI logic: parse_intent · generate_route · generate_clues
│   ├── requirements.txt # Python dependencies
│   └── tests/
│       └── test_api.py  # pytest suite (health, route, agent, unit tests)
├── frontend/
│   ├── index.html       # Single-page app shell
│   ├── style.css        # Dark-mode UI
│   └── app.js           # Fetch client + pipeline trace renderer
└── demo/
    └── README.md        # ASCII mockup · pipeline diagram · multi-turn example
```

---

## Quick Start

### Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.10 |
| pip | 23+ |

### 1 — Clone

```bash
git clone https://github.com/uptry/GeoAgent.git
cd GeoAgent
```

### 2 — Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3 — Start the backend

```bash
uvicorn main:app --reload
# API server:  http://localhost:8000
# OpenAPI docs: http://localhost:8000/docs
```

### 4 — Open the frontend

No build step needed.  Open `frontend/index.html` directly in a browser:

```bash
# macOS
open ../frontend/index.html

# Linux
xdg-open ../frontend/index.html

# Windows
start ../frontend/index.html
```

Or serve with Python's built-in HTTP server:

```bash
cd ../frontend
python -m http.server 3000
# Open http://localhost:3000
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/health` | Liveness check |
| `POST` | `/api/route`  | Step 2 only — route planning for a city |
| `POST` | `/api/clues`  | Step 3 only — clue generation for a stop list |
| `POST` | `/api/agent`  | Full pipeline (Steps 1–4) — main endpoint |

### Full pipeline — `/api/agent`

**Request**

```json
{
  "city": "Paris",
  "num_stops": 3,
  "conversation_history": []
}
```

**Response**

```json
{
  "route": {
    "city": "Paris",
    "stops": [
      { "name": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "type": "monument" }
    ],
    "summary": "Your GeoAgent route through Paris visits 3 locations…",
    "note": ""
  },
  "clues": [
    {
      "stop_name": "Eiffel Tower",
      "lat": 48.8584,
      "lon": 2.2945,
      "clue": "Where iron giants touch the sky, seek the shadow at noon."
    }
  ],
  "pipeline_steps": [
    { "step": "intent_parsing",     "status": "completed", "output": { "city": "Paris", "num_stops": 3, "exploration_style": "cultural" } },
    { "step": "route_planning",     "status": "completed", "output": { "stops_planned": 3 } },
    { "step": "clue_generation",    "status": "completed", "output": { "clues_generated": 3 } },
    { "step": "dialogue_synthesis", "status": "completed", "output": { "message": "I've planned a cultural route through Paris…" } }
  ],
  "conversation_history": [
    { "role": "user",      "content": "Plan a cultural route in Paris" },
    { "role": "assistant", "content": "I've planned a cultural route through Paris with 3 stops…" }
  ]
}
```

---

## Running the Tests

```bash
cd backend
python -m pytest tests/ -v
```

The suite covers:

- Health endpoint
- Route generation (known & unknown cities, edge cases, validation)
- Full agent endpoint (basic call, multi-turn history)
- Unit tests for `parse_intent`, `generate_route`, `generate_clues`

---

## Replacing the Mock Engine with a Real LLM

Open `backend/agent.py`.  Each pipeline function has a docstring that
describes exactly what prompt and schema to use when calling an LLM.
Replace the function body with your LLM call — no other file needs to
change.

```
parse_intent()    → structured-output prompt → intent JSON
generate_route()  → tool-use / RAG call      → ordered stop list
generate_clues()  → creative generation      → riddle per waypoint
```

---

## Demo

See [`demo/README.md`](demo/README.md) for an ASCII mockup of the UI,
a detailed pipeline flow diagram, and a multi-turn dialogue example.

---

## License

MIT
