"""
Tests for the GeoAgent backend.
"""

import sys
import os

# Ensure the backend package is importable when running pytest from any directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from main import app
from agent import generate_clues, generate_route

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /api/route
# ---------------------------------------------------------------------------


def test_route_known_city():
    response = client.post("/api/route", json={"city": "Paris", "num_stops": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert len(data["stops"]) == 3
    for stop in data["stops"]:
        assert "name" in stop
        assert "lat" in stop
        assert "lon" in stop


def test_route_unknown_city():
    response = client.post("/api/route", json={"city": "Atlantis", "num_stops": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Atlantis"
    assert len(data["stops"]) == 2
    assert data["note"] != ""


def test_route_default_stops():
    response = client.post("/api/route", json={"city": "London"})
    assert response.status_code == 200
    assert len(response.json()["stops"]) == 4


def test_route_empty_city():
    response = client.post("/api/route", json={"city": "   ", "num_stops": 3})
    assert response.status_code == 400


def test_route_max_stops():
    response = client.post("/api/route", json={"city": "Tokyo", "num_stops": 6})
    assert response.status_code == 200
    assert len(response.json()["stops"]) <= 6


def test_route_exceeds_max_stops():
    response = client.post("/api/route", json={"city": "Rome", "num_stops": 10})
    assert response.status_code == 422  # Pydantic validation error


# ---------------------------------------------------------------------------
# /api/agent
# ---------------------------------------------------------------------------


def test_agent_basic():
    response = client.post("/api/agent", json={"city": "New York", "num_stops": 2})
    assert response.status_code == 200
    data = response.json()
    assert "route" in data
    assert "clues" in data
    assert "conversation_history" in data
    assert len(data["clues"]) == 2


def test_agent_with_history():
    history = [{"role": "user", "content": "Hello"}]
    response = client.post(
        "/api/agent",
        json={"city": "Paris", "num_stops": 2, "conversation_history": history},
    )
    assert response.status_code == 200
    conv = response.json()["conversation_history"]
    # Original message + new user turn + assistant turn
    assert len(conv) == 3


def test_agent_empty_city():
    response = client.post("/api/agent", json={"city": "", "num_stops": 2})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Agent module unit tests
# ---------------------------------------------------------------------------


def test_generate_route_structure():
    result = generate_route("London", 3)
    assert result["city"] == "London"
    assert len(result["stops"]) == 3
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


def test_generate_clues_structure():
    stops = [
        {"name": "Test Stop", "lat": 51.5, "lon": -0.1, "type": "monument"},
        {"name": "Another Stop", "lat": 48.8, "lon": 2.3, "type": "park"},
    ]
    clues = generate_clues(stops, "TestCity")
    assert len(clues) == 2
    for clue in clues:
        assert "stop_name" in clue
        assert "lat" in clue
        assert "lon" in clue
        assert "clue" in clue
        assert isinstance(clue["clue"], str)
        assert len(clue["clue"]) > 0


def test_generate_route_unknown_city():
    result = generate_route("UnknownCity", 3)
    assert result["city"] == "Unknowncity"
    assert len(result["stops"]) == 3
    assert result["note"] != ""


def test_generate_clues_unknown_type():
    stops = [{"name": "Mystery Stop", "lat": 0.0, "lon": 0.0, "type": "unknown_type"}]
    clues = generate_clues(stops, "Somewhere")
    assert len(clues) == 1
    assert isinstance(clues[0]["clue"], str)
