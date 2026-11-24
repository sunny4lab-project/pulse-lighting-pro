"""Offline fixture identification from imported Open Fixture Library profiles."""
import json
from pathlib import Path
from difflib import SequenceMatcher

def load_profile(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data.get("name"), str) or not isinstance(data.get("modes"), list):
        raise ValueError("Expected an Open Fixture Library fixture JSON file")
    modes = []
    for mode in data["modes"]:
        channels = mode.get("channels", [])
        if isinstance(channels, list) and 1 <= len(channels) <= 512:
            modes.append({"name": mode.get("name", "Unnamed"), "channels": channels,
                          "footprint": len(channels)})
    if not modes:
        raise ValueError("No valid DMX modes")
    return {"name": data["name"], "categories": data.get("categories", []),
            "modes": modes, "source": str(path), "manufacturer": Path(path).parent.name}

def match_profiles(profiles, query, footprint=None):
    query = query.strip().casefold()
    results = []
    for p in profiles:
        for m in p["modes"]:
            if footprint is not None and m["footprint"] != footprint:
                continue
            name = (p["manufacturer"]+" "+p["name"]).casefold()
            score = (1.0 if query and query in name else SequenceMatcher(None, query, name).ratio()) if query else 0
            results.append((score, p, m))
    return sorted(results, key=lambda r: (-r[0], r[1]["name"], r[2]["name"]))

def allocate(count, footprint):
    if not 1 <= count <= 256 or not 1 <= footprint <= 512:
        raise ValueError("Count must be 1–256 and footprint 1–512")
    per = 512 // footprint
    return [(i//per+1, (i%per)*footprint+1) for i in range(count)]
