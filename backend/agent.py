"""
GeoAgent AI logic module.

Provides mock LLM-based route planning and geocaching clue generation.
This module is designed to be easily replaced with a real LLM (e.g. MiMo API).
"""

import random
from typing import Any

# ---------------------------------------------------------------------------
# Landmark data used by the mock "LLM"
# ---------------------------------------------------------------------------

CITY_LANDMARKS: dict[str, list[dict[str, Any]]] = {
    "paris": [
        {"name": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "type": "monument"},
        {"name": "Louvre Museum", "lat": 48.8606, "lon": 2.3376, "type": "museum"},
        {"name": "Notre-Dame Cathedral", "lat": 48.8530, "lon": 2.3499, "type": "church"},
        {"name": "Arc de Triomphe", "lat": 48.8738, "lon": 2.2950, "type": "monument"},
        {"name": "Sacré-Cœur Basilica", "lat": 48.8867, "lon": 2.3431, "type": "church"},
        {"name": "Musée d'Orsay", "lat": 48.8600, "lon": 2.3266, "type": "museum"},
    ],
    "london": [
        {"name": "Tower of London", "lat": 51.5081, "lon": -0.0759, "type": "castle"},
        {"name": "Buckingham Palace", "lat": 51.5014, "lon": -0.1419, "type": "palace"},
        {"name": "Big Ben", "lat": 51.5007, "lon": -0.1246, "type": "monument"},
        {"name": "British Museum", "lat": 51.5194, "lon": -0.1270, "type": "museum"},
        {"name": "Tower Bridge", "lat": 51.5055, "lon": -0.0754, "type": "bridge"},
        {"name": "Hyde Park", "lat": 51.5073, "lon": -0.1657, "type": "park"},
    ],
    "new york": [
        {"name": "Statue of Liberty", "lat": 40.6892, "lon": -74.0445, "type": "monument"},
        {"name": "Central Park", "lat": 40.7851, "lon": -73.9683, "type": "park"},
        {"name": "Empire State Building", "lat": 40.7484, "lon": -73.9857, "type": "skyscraper"},
        {"name": "Brooklyn Bridge", "lat": 40.7061, "lon": -73.9969, "type": "bridge"},
        {"name": "Times Square", "lat": 40.7580, "lon": -73.9855, "type": "plaza"},
        {"name": "Metropolitan Museum of Art", "lat": 40.7794, "lon": -73.9632, "type": "museum"},
    ],
    "tokyo": [
        {"name": "Senso-ji Temple", "lat": 35.7148, "lon": 139.7967, "type": "temple"},
        {"name": "Tokyo Tower", "lat": 35.6586, "lon": 139.7454, "type": "monument"},
        {"name": "Shibuya Crossing", "lat": 35.6595, "lon": 139.7004, "type": "plaza"},
        {"name": "Shinjuku Gyoen", "lat": 35.6851, "lon": 139.7100, "type": "park"},
        {"name": "Meiji Shrine", "lat": 35.6764, "lon": 139.6993, "type": "shrine"},
        {"name": "Tsukiji Outer Market", "lat": 35.6654, "lon": 139.7707, "type": "market"},
    ],
    "rome": [
        {"name": "Colosseum", "lat": 41.8902, "lon": 12.4922, "type": "monument"},
        {"name": "Vatican Museums", "lat": 41.9065, "lon": 12.4536, "type": "museum"},
        {"name": "Trevi Fountain", "lat": 41.9009, "lon": 12.4833, "type": "fountain"},
        {"name": "Pantheon", "lat": 41.8986, "lon": 12.4769, "type": "monument"},
        {"name": "Roman Forum", "lat": 41.8925, "lon": 12.4853, "type": "ruins"},
        {"name": "Borghese Gallery", "lat": 41.9142, "lon": 12.4922, "type": "museum"},
    ],
}

# Clue templates keyed by landmark type
CLUE_TEMPLATES: dict[str, list[str]] = {
    "monument": [
        "Where iron giants touch the sky, seek the shadow at {hour}.",
        "A triumph of stone and history — find the plaque on the north side.",
        "Generations have gathered at this {type}; look beneath the third step.",
    ],
    "museum": [
        "Art whispers secrets; ask the statue near the main entrance.",
        "Knowledge lives in these halls — the cache hides behind the oldest exhibit.",
        "Step inside history; look under the bench facing the courtyard.",
    ],
    "church": [
        "Faith carved in stone — follow the mosaic path to its end.",
        "The bells have tolled for centuries; count the arches and find the fifth.",
        "Sacred ground holds many secrets; seek the gargoyle facing east.",
    ],
    "castle": [
        "Walls that once held kings — find the loose stone near the drawbridge.",
        "A fortress of legend; trace the moat to the old postern gate.",
        "Ravens guard this place; follow their gaze to the hidden nook.",
    ],
    "palace": [
        "Royalty once walked these gardens; find the sundial in the east wing.",
        "Gilded gates mark the entrance — the cache is three paces left of the crest.",
        "Where pageantry meets history, look beneath the ceremonial flagpole.",
    ],
    "bridge": [
        "Two shores meet here; descend to the pier at the midpoint.",
        "Cables or stone, this bridge spans time — find the plaque on the eastern pillar.",
        "Cross halfway, then look down — the cache rests on the third bolt from the top.",
    ],
    "park": [
        "Nature's refuge in the city — the cache hides in the hollow oak near the fountain.",
        "Follow the main path until you see three benches in a row; it's under the middle one.",
        "Where families gather on weekends — find the big rock near the pond's north shore.",
    ],
    "skyscraper": [
        "A needle that pierces the clouds; at street level, find the cornerstone.",
        "Look up, then look down — the cache is at the base of the eastern wall.",
        "Glass and steel tower above; the clue lives in the lobby garden.",
    ],
    "plaza": [
        "Crowds swirl like a living map — stand at the centre and face north.",
        "Neon and footsteps fill this square; the cache rests by the info board.",
        "A crossroads of the world; find the time capsule near the old lamppost.",
    ],
    "temple": [
        "Incense and centuries of prayer — three lanterns mark the path; take the middle one.",
        "Sacred smoke guides the way; look behind the offering table on the right.",
        "Silence speaks loudest here; find the cache under the moss-covered stone.",
    ],
    "shrine": [
        "Torii gates frame a path of faith; at the final gate, look left.",
        "The kami dwell here — find the smooth stone beside the purification fountain.",
        "Prayers written on wood surround you; the cache is tied to the oldest post.",
    ],
    "fountain": [
        "Coins and wishes fill these waters; circle the fountain and find the loose tile.",
        "Where water sings, secrets hide — look in the shadow at noon.",
        "Toss a coin and make a wish, then check behind the north-facing cherub.",
    ],
    "ruins": [
        "Ghosts of empire linger here — count the fallen columns; the cache is near the seventh.",
        "Ancient stones remember everything; find the inscription on the arch facing west.",
        "Time has crumbled these walls but the cache endures — look beneath the capstone.",
    ],
    "market": [
        "Fresh flavours fill the air; find the cache behind the oldest vendor stall.",
        "Bargains abound but one prize is hidden — ask the fish monger's direction then look down.",
        "The market never sleeps; find the plaque at the main entrance, then pace ten steps south.",
    ],
}

DEFAULT_CLUE_TEMPLATES = [
    "A well-known spot in {city} — look around for something that doesn't quite fit.",
    "Locals pass this daily without a second glance; you'll find the cache nearby.",
    "History meets the present here; the cache is hidden in plain sight.",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_route(city: str, num_stops: int = 4) -> dict[str, Any]:
    """
    Generate a sightseeing route for the given city.

    Returns a dict with:
      - city: normalised city name
      - stops: list of landmark dicts
      - summary: human-readable description
    """
    city_key = city.strip().lower()
    landmarks = CITY_LANDMARKS.get(city_key)

    if landmarks:
        stops = random.sample(landmarks, min(num_stops, len(landmarks)))
        note = ""
    else:
        # Fallback for unknown cities
        stops = _generate_generic_stops(city, num_stops)
        note = f"No landmark data found for '{city}'. Showing generic waypoints."

    return {
        "city": city.strip().title(),
        "stops": stops,
        "summary": _build_route_summary(city.strip().title(), stops),
        "note": note,
    }


def generate_clues(stops: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    """
    Generate a geocaching clue for each stop on the route.

    Returns a list of dicts with:
      - stop_name: landmark name
      - lat / lon: coordinates
      - clue: the geocaching clue text
    """
    result = []
    for stop in stops:
        landmark_type = stop.get("type", "monument")
        templates = CLUE_TEMPLATES.get(landmark_type, DEFAULT_CLUE_TEMPLATES)
        clue_text = random.choice(templates).format(
            city=city, type=landmark_type, hour="noon"
        )
        result.append(
            {
                "stop_name": stop["name"],
                "lat": stop["lat"],
                "lon": stop["lon"],
                "clue": clue_text,
            }
        )
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _generate_generic_stops(city: str, num_stops: int) -> list[dict[str, Any]]:
    """Return placeholder stops for cities not in our database.

    Coordinates are intentionally randomised as stand-ins; replace with a
    geocoding call (e.g. Nominatim) when integrating a real LLM backend.
    """
    generic_types = ["monument", "museum", "park", "bridge"]
    stops = []
    for i in range(num_stops):
        stops.append(
            {
                "name": f"{city.strip().title()} Landmark {i + 1}",
                "lat": round(random.uniform(-90, 90), 4),
                "lon": round(random.uniform(-180, 180), 4),
                "type": generic_types[i % len(generic_types)],
            }
        )
    return stops


def _build_route_summary(city: str, stops: list[dict[str, Any]]) -> str:
    stop_names = [s["name"] for s in stops]
    if len(stop_names) == 1:
        route_str = stop_names[0]
    elif len(stop_names) == 2:
        route_str = f"{stop_names[0]} and {stop_names[1]}"
    else:
        route_str = ", ".join(stop_names[:-1]) + f", and {stop_names[-1]}"
    return (
        f"Your GeoAgent route through {city} visits {len(stops)} location"
        f"{'s' if len(stops) != 1 else ''}: {route_str}. "
        "Each stop comes with a geocaching clue to make the journey more adventurous!"
    )
