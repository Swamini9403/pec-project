"""
dataset_loader.py
-----------------
Loads marathi_math_dataset.jsonl and pythagoras_dataset.jsonl.
Provides keyword + fuzzy matching to retrieve best responses.
"""

import os
import json
import re
import difflib
import random

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")

_math_data: list[dict] = []
_pythagoras_data: list[dict] = []
_loaded = False


def _load():
    global _math_data, _pythagoras_data, _loaded
    if _loaded:
        return

    def read_jsonl(filename):
        path = os.path.join(DATASET_DIR, filename)
        rows = []
        if not os.path.exists(path):
            print(f"[DATASET] Warning: {path} not found.")
            return rows
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    _math_data = read_jsonl("marathi_math_dataset.jsonl")
    _pythagoras_data = read_jsonl("pythagoras_dataset.jsonl")
    _loaded = True

    # Sanity check — warn if dataset looks like old one-liners
    if _pythagoras_data:
        sample = _pythagoras_data[0]["response"]
        if len(sample) < 60:
            print("[DATASET] WARNING: Pythagoras dataset looks like old short responses!")
            print(f"[DATASET] Sample: {sample}")
        else:
            print(f"[DATASET] Loaded {len(_math_data)} math + {len(_pythagoras_data)} pythagoras entries. ✓")


def reload():
    """Force reload datasets."""
    global _loaded
    _loaded = False
    _load()


def _best_match(query: str, data: list[dict]) -> str | None:
    """Return best matching response from dataset using keyword + fuzzy matching."""
    if not data:
        return None

    # 1. Exact match
    for d in data:
        if d["instruction"] == query:
            return d["response"]

    # 2. Keyword match — find entries whose instruction is contained in query or vice versa
    candidates = [d for d in data if d["instruction"] in query or query in d["instruction"]]
    if candidates:
        return random.choice(candidates)["response"]

    # 3. Fuzzy match
    instructions = [d["instruction"] for d in data]
    matches = difflib.get_close_matches(query, instructions, n=3, cutoff=0.35)
    if matches:
        matched = [d for d in data if d["instruction"] in matches]
        if matched:
            return random.choice(matched)["response"]

    return None


def get_math_response(instruction: str) -> str:
    """Retrieve best math dataset response for the given instruction."""
    _load()
    result = _best_match(instruction, _math_data)
    return result or random.choice(_math_data)["response"] if _math_data else "माफ करा, उत्तर सापडले नाही."


def get_pythagoras_response(mode: str) -> str:
    """
    Retrieve a Pythagoras dataset response.
    mode: 'explain' | 'story' | 'example' | 'quiz'
    """
    _load()

    mode_map = {
        "explain": "पायथागोरस समजाव",
        "story":   "गोष्ट वापरून पायथागोरस समजाव",
        "example": "उदाहरण दे",
        "quiz":    "पायथागोरस quiz दे",
    }

    query = mode_map.get(mode, "पायथागोरस समजाव")
    candidates = [d for d in _pythagoras_data if d["instruction"] == query]

    if candidates:
        return random.choice(candidates)["response"]

    # Fallback: any pythagoras entry
    if _pythagoras_data:
        return random.choice(_pythagoras_data)["response"]

    return "पायथागोरस प्रमेयानुसार a² + b² = c² असते."
