"""
GeoAgent FastAPI backend.

Agent pipeline (invoked by POST /api/agent):
  Step 1 – Intent Parsing     : extract city, stops, exploration style
  Step 2 – Route Planning     : select & order landmarks
  Step 3 – Clue Generation    : write geocaching riddles for each waypoint
  Step 4 – Dialogue Synthesis : compose conversational response + update history

Individual pipeline steps are also exposed as standalone endpoints:
  POST /api/route   – Step 2 only (route planning)
  POST /api/clues   – Step 3 only (clue generation)
  GET  /api/health  – liveness check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import generate_clues, generate_route, parse_intent

app = FastAPI(
    title="GeoAgent API",
    description="AI-powered route planning and geocaching clue generation.",
    version="1.0.0",
)

# Allow all origins for development; tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class RouteRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Paris"})
    num_stops: int = Field(default=4, ge=1, le=6)


class AgentRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "London"})
    num_stops: int = Field(default=4, ge=1, le=6)
    conversation_history: list[dict] = Field(
        default_factory=list,
        description="Optional prior turns for multi-turn interaction.",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/route")
def route_endpoint(req: RouteRequest) -> dict:
    """Return a sightseeing route for the requested city."""
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="City name must not be empty.")
    return generate_route(req.city, req.num_stops)


@app.post("/api/clues")
def clues_endpoint(stops: list[dict], city: str = "Unknown") -> list[dict]:
    """Return geocaching clues for the provided stops."""
    if not stops:
        raise HTTPException(status_code=400, detail="Stops list must not be empty.")
    return generate_clues(stops, city)


@app.post("/api/agent")
def agent_endpoint(req: AgentRequest) -> dict:
    """
    Main Agent endpoint — runs the full four-step pipeline in one call.

    Pipeline:
      1. Intent Parsing     – normalise city name, infer exploration style
      2. Route Planning     – select & order the best landmarks
      3. Clue Generation    – generate a geocaching riddle per waypoint
      4. Dialogue Synthesis – compose a conversational reply & update history

    Accepts optional conversation_history to support multi-turn interactions:
    pass the conversation_history from a previous response back here and the
    agent will treat it as prior context.
    """
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="City name must not be empty.")

    # ── Step 1: Intent Parsing ───────────────────────────────────────────────
    intent = parse_intent(req.city, req.num_stops)

    # ── Step 2: Route Planning ───────────────────────────────────────────────
    route = generate_route(req.city, req.num_stops)

    # ── Step 3: Clue Generation ──────────────────────────────────────────────
    clues = generate_clues(route["stops"], route["city"])

    # ── Step 4: Dialogue Synthesis ───────────────────────────────────────────
    assistant_message = {
        "role": "assistant",
        "content": (
            f"I've planned a {intent['exploration_style']} route through "
            f"{route['city']} with {len(route['stops'])} stops and generated "
            "geocaching clues for each one. Happy exploring!"
        ),
    }
    updated_history = req.conversation_history + [
        {"role": "user", "content": f"Plan a route in {req.city}"},
        assistant_message,
    ]

    # pipeline_steps lets callers (and the UI) trace how the agent reasoned
    pipeline_steps = [
        {
            "step": "intent_parsing",
            "status": "completed",
            "output": {
                "city": intent["city_display"],
                "num_stops": intent["num_stops"],
                "exploration_style": intent["exploration_style"],
            },
        },
        {
            "step": "route_planning",
            "status": "completed",
            "output": {"stops_planned": len(route["stops"])},
        },
        {
            "step": "clue_generation",
            "status": "completed",
            "output": {"clues_generated": len(clues)},
        },
        {
            "step": "dialogue_synthesis",
            "status": "completed",
            "output": {"message": assistant_message["content"]},
        },
    ]

    return {
        "route": route,
        "clues": clues,
        "conversation_history": updated_history,
        "pipeline_steps": pipeline_steps,
    }
