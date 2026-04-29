# GeoAgent – Demo

This directory contains demo assets for the GeoAgent project.

## UI Screenshot

> **Live demo** — run the backend and open `frontend/index.html` in a browser.

```
┌─────────────────────────────────────────────────────────────────┐
│  🌍 GeoAgent                                                    │
│  AI-powered sightseeing routes & geocaching clues               │
├─────────────────────────────────────────────────────────────────┤
│  Plan Your Adventure                                            │
│  City  [ Paris                         ]                        │
│  Stops ──────────────●──────── 4                                │
│  [ Generate Route & Clues ]                                     │
├─────────────────────────────────────────────────────────────────┤
│  🤖 Agent Reasoning Trace                                       │
│  🔍 Intent Parsing     ✓ completed  city: Paris · num_stops: 4  │
│  🗺️ Route Planning     ✓ completed  stops_planned: 4            │
│  🔑 Clue Generation    ✓ completed  clues_generated: 4          │
│  💬 Dialogue Synthesis ✓ completed  message: I've planned…      │
├─────────────────────────────────────────────────────────────────┤
│  Route: Paris                                                   │
│  Your GeoAgent route through Paris visits 4 locations…         │
│  ① Eiffel Tower        48.8584°, 2.2945°                        │
│     🗺 Clue: Where iron giants touch the sky…                   │
│  ② Louvre Museum       48.8606°, 2.3376°                        │
│     🗺 Clue: Art whispers secrets; ask the statue…              │
│  ③ Arc de Triomphe     48.8738°, 2.2950°                        │
│     🗺 Clue: A triumph of stone and history…                    │
│  ④ Sacré-Cœur Basilica 48.8867°, 2.3431°                        │
│     🗺 Clue: Faith carved in stone — follow the mosaic path…   │
├─────────────────────────────────────────────────────────────────┤
│  Conversation History                                           │
│  user: Plan a cultural route in Paris                           │
│  assistant: I've planned a cultural route through Paris…        │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Pipeline Flow

```
User types "Paris" + selects 4 stops
         │
         ▼
┌─────────────────────┐
│  1. Intent Parsing  │  city="Paris", style="cultural"
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  2. Route Planning  │  Eiffel Tower, Louvre, Arc de Triomphe, Sacré-Cœur
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  3. Clue Generation │  Riddle-style hint per waypoint
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│  4. Dialogue Synthesis│  Conversational reply + history update
└──────────────────────┘
         │
         ▼
    JSON response returned to browser
```

## Multi-turn Dialogue

Each call to `/api/agent` accepts a `conversation_history` array.
Pass the history from the previous response back to simulate a
multi-turn conversation:

```json
POST /api/agent
{
  "city": "Paris",
  "num_stops": 2,
  "conversation_history": [
    { "role": "user",      "content": "Plan a cultural route in London" },
    { "role": "assistant", "content": "I've planned a cultural route through London…" }
  ]
}
```
