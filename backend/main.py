"""
GeoAgent FastAPI backend.

Endpoints:
  POST /api/route   – generate a sightseeing route for a city
  POST /api/clues   – generate geocaching clues for a list of stops
  POST /api/agent   – single combined endpoint (route + clues in one call)
  GET  /api/health  – liveness check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import generate_clues, generate_route

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
    Combined endpoint: generate route + clues in a single call.

    Accepts optional conversation_history to support multi-turn interactions.
    """
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="City name must not be empty.")

    route = generate_route(req.city, req.num_stops)
    clues = generate_clues(route["stops"], route["city"])

    # Build a new conversation turn
    assistant_message = {
        "role": "assistant",
        "content": (
            f"I've planned a route through {route['city']} with "
            f"{len(route['stops'])} stops and generated geocaching clues for each one."
        ),
    }
    updated_history = req.conversation_history + [
        {"role": "user", "content": f"Plan a route in {req.city}"},
        assistant_message,
    ]

    return {
        "route": route,
        "clues": clues,
        "conversation_history": updated_history,
    }
