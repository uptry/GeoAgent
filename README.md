# GeoAgent 🌍

An AI-powered sightseeing route planner and geocaching clue generator — a minimal full-stack MVP that demonstrates a multi-turn AI Agent architecture.

---

## Project Overview

GeoAgent lets a user type in any city name and instantly receive:

1. **A sightseeing route** – a curated list of notable landmarks with coordinates.
2. **Geocaching clues** – a riddle-style hint for finding a hidden "cache" at each stop.
3. **Conversation history** – each interaction is stored as a turn, giving the app a multi-turn AI Agent structure that is ready to be extended with a real LLM.

The AI logic currently uses a mock engine (pre-seeded landmark data + randomised clue templates).  
The engine is isolated in `backend/agent.py` and can be swapped for a real LLM (e.g. **MiMo API**) without touching any other file.

---

## Repository Structure

```
GeoAgent/
├── backend/
│   ├── main.py          # FastAPI application & REST endpoints
│   ├── agent.py         # AI logic (mock LLM – route planning & clue generation)
│   ├── requirements.txt # Python dependencies
│   └── tests/
│       └── test_api.py  # pytest test suite
└── frontend/
    ├── index.html        # Single-page application shell
    ├── style.css         # Dark-mode UI styles
    └── app.js            # Fetch-based client logic
```

---

## Quick Start

### Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.10 |
| pip | 23+ |

> A virtual-environment tool (`venv` or `conda`) is recommended but not required.

---

### 1 – Clone the repository

```bash
git clone https://github.com/uptry/GeoAgent.git
cd GeoAgent
```

### 2 – Set up the backend

```bash
cd backend
python -m venv .venv          # optional but recommended
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3 – Start the backend server

```bash
uvicorn main:app --reload
# Server starts at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### 4 – Open the frontend

No build step is needed.  Open `frontend/index.html` directly in a browser:

```bash
# macOS
open ../frontend/index.html

# Linux
xdg-open ../frontend/index.html

# Windows
start ../frontend/index.html
```

Or serve it with any static-file server, e.g.:

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
| `POST` | `/api/route`  | Generate a route for a city |
| `POST` | `/api/clues`  | Generate clues for a list of stops |
| `POST` | `/api/agent`  | Combined route + clues (main endpoint) |

Full interactive documentation is available at **`http://localhost:8000/docs`** when the server is running.

### Example – `/api/agent`

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
      { "name": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "type": "monument" },
      ...
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
    },
    ...
  ],
  "conversation_history": [
    { "role": "user", "content": "Plan a route in Paris" },
    { "role": "assistant", "content": "I've planned a route through Paris with 3 stops…" }
  ]
}
```

---

## Running the Tests

```bash
cd backend
python -m pytest tests/ -v
```

All tests are in `backend/tests/test_api.py` and cover:

- Health endpoint
- Route generation (known & unknown cities, edge cases)
- Agent endpoint (basic call, multi-turn history, validation)
- Unit tests for `agent.py` functions

---

## Replacing the Mock AI with a Real LLM

Open `backend/agent.py` and replace the body of `generate_route` and `generate_clues` with calls to your preferred LLM provider (e.g. MiMo API, OpenAI, Anthropic).  
The rest of the application (`main.py`, frontend) requires no changes.

---

## License

MIT