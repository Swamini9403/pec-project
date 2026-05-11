"""
intent.py
---------
Rule-based intent detection using Marathi keyword matching.
Fully offline — no ML needed.
"""

# ── Intent labels ──────────────────────────────────────────────────────────────
INTENT_MODE_ARITH   = "mode_arith"      # switch to arithmetic mode
INTENT_MODE_PYTH    = "mode_pyth"       # switch to pythagoras mode
INTENT_CALCULATE    = "calculate"
INTENT_EXPLAIN      = "explain"
INTENT_STORY        = "story"
INTENT_QUIZ         = "quiz"
INTENT_REPEAT       = "repeat"
INTENT_PYTHAGORAS   = "pythagoras"      # legacy — kept for compat
INTENT_PYTH_EXPLAIN = "pyth_explain"
INTENT_PYTH_STORY   = "pyth_story"
INTENT_PYTH_EXAMPLE = "pyth_example"
INTENT_PYTH_QUIZ    = "pyth_quiz"
INTENT_PYTH_SOLVE   = "pyth_solve"
INTENT_UNKNOWN      = "unknown"

# ── Keyword lists ──────────────────────────────────────────────────────────────

# Mode switch
MODE_ARITH_KEYWORDS = ["अंकगणित", "arithmetic", "गणित मोड", "बेरीज मोड"]
MODE_PYTH_KEYWORDS  = ["पायथागोरस मोड", "भूमिती मोड", "geometry mode",
                       "पायथागोरस शिकव", "पायथागोरस सुरू"]

# Pythagoras topic keywords (used inside Pythagoras mode OR with explicit mention)
PYTH_KEYWORDS = ["पायथागोरस", "त्रिकोण", "कर्ण", "pythagoras", "hypotenuse", "बाजू"]
PYTH_CONTEXT_PHRASES = ["कोणता नियम", "हा नियम", "हे प्रमेय", "कोणते प्रमेय"]

# Quiz
QUIZ_STOP_KEYWORDS  = ["थांब", "बंद", "stop", "क्विझ बंद", "परीक्षा बंद", "exit", "quit"]
QUIZ_START_KEYWORDS = [
    "quiz", "क्विझ", "क्विक", "क्वीझ", "क्वीज", "क्विज",
    "परीक्षा", "प्रश्न विचार", "टेस्ट", "test",
]

# Example
EXAMPLE_KEYWORDS = ["उदाहरण", "example", "दाखव", "त्रिकूट"]

# Arithmetic operators
ARITH_KEYWORDS = [
    "बेरीज", "वजाबाकी", "गुणाकार", "भागाकार",
    "जोड", "वजा", "गुणा", "भागिले", "अधिक", "गुणिले",
    "+", "×", "÷", "*", "किती", "उत्तर",
]


def _is_pythagoras_topic(text: str) -> bool:
    return (any(k in text for k in PYTH_KEYWORDS)
            or any(p in text for p in PYTH_CONTEXT_PHRASES))


def _has_marathi_numbers(text: str) -> bool:
    marathi_nums = [
        "एक", "दोन", "तीन", "चार", "पाच", "सहा", "सात", "आठ", "नऊ", "दहा",
        "अकरा", "बारा", "तेरा", "चौदा", "पंधरा", "वीस", "तीस", "शंभर",
    ]
    return any(n in text for n in marathi_nums)


def detect_intent(text: str, mode: str = "general") -> str:
    """
    Detect intent from user text.

    mode: 'general' | 'arithmetic' | 'pythagoras'
    When mode is set, ambiguous commands are resolved in favour of that mode.

    Returns one of the INTENT_* constants.
    """
    import re

    # ── Universal: repeat ─────────────────────────────────────────────────────
    if any(k in text for k in ["परत सांगा", "परत", "repeat", "पुन्हा सांगा", "पुन्हा"]):
        return INTENT_REPEAT

    # ── Universal: mode switch ────────────────────────────────────────────────
    if any(k in text for k in MODE_ARITH_KEYWORDS):
        return INTENT_MODE_ARITH
    if any(k in text for k in MODE_PYTH_KEYWORDS):
        return INTENT_MODE_PYTH
    # Plain "पायथागोरस" alone → switch to Pythagoras mode
    if text.strip() in ["पायथागोरस", "pythagoras"]:
        return INTENT_MODE_PYTH

    # ── Universal: quiz stop ──────────────────────────────────────────────────
    if any(k in text for k in QUIZ_STOP_KEYWORDS):
        if not any(k in text for k in QUIZ_START_KEYWORDS):
            return INTENT_REPEAT  # handled as quiz-stop in server

    # ── Quiz start ────────────────────────────────────────────────────────────
    if any(k in text for k in QUIZ_START_KEYWORDS):
        if mode == "pythagoras" or _is_pythagoras_topic(text):
            return INTENT_PYTH_QUIZ
        return INTENT_QUIZ

    # ══════════════════════════════════════════════════════════════════════════
    # PYTHAGORAS MODE — all ambiguous commands resolve to Pythagoras
    # ══════════════════════════════════════════════════════════════════════════
    if mode == "pythagoras":
        # Story
        if any(k in text for k in ["गोष्ट", "गोष्टीतून", "कथा", "story"]):
            return INTENT_PYTH_STORY
        # Example
        if any(k in text for k in EXAMPLE_KEYWORDS):
            return INTENT_PYTH_EXAMPLE
        # Explain
        if any(k in text for k in ["समजाव", "समजावून", "explain", "सांग",
                                    "प्रमेय", "काय", "कसे", "शिकव", "सांगा"]):
            return INTENT_PYTH_EXPLAIN
        # Numbers → solve
        if re.search(r'\d', text) or _has_marathi_numbers(text):
            return INTENT_PYTH_SOLVE
        # Default in Pythagoras mode
        return INTENT_PYTH_EXPLAIN

    # ══════════════════════════════════════════════════════════════════════════
    # ARITHMETIC MODE — all ambiguous commands resolve to arithmetic
    # ══════════════════════════════════════════════════════════════════════════
    if mode == "arithmetic":
        if any(k in text for k in ["गोष्टीतून", "गोष्ट", "कथा", "story"]):
            return INTENT_STORY
        if any(k in text for k in ["समजाव", "समजावून", "explain", "कसे", "का"]):
            return INTENT_EXPLAIN
        # Numbers → calculate
        if re.search(r'\d', text) or _has_marathi_numbers(text) or any(k in text for k in ARITH_KEYWORDS):
            return INTENT_CALCULATE
        return INTENT_UNKNOWN

    # ══════════════════════════════════════════════════════════════════════════
    # GENERAL MODE — explicit keywords required
    # ══════════════════════════════════════════════════════════════════════════

    # Standalone example → Pythagoras context
    if any(k in text for k in EXAMPLE_KEYWORDS) and not any(k in text for k in ARITH_KEYWORDS):
        return INTENT_PYTH_EXAMPLE

    # Pythagoras topic explicitly mentioned
    if _is_pythagoras_topic(text):
        if any(k in text for k in ["गोष्ट", "गोष्टीतून", "कथा", "story"]):
            return INTENT_PYTH_STORY
        if any(k in text for k in ["समजाव", "समजावून", "explain", "सांग",
                                    "प्रमेय", "काय", "कसे"]):
            return INTENT_PYTH_EXPLAIN
        if any(k in text for k in EXAMPLE_KEYWORDS):
            return INTENT_PYTH_EXAMPLE
        if re.search(r'\d', text) or _has_marathi_numbers(text):
            return INTENT_PYTH_SOLVE
        return INTENT_PYTH_EXPLAIN

    # Story
    if any(k in text for k in ["गोष्टीतून", "गोष्ट", "कथा", "story"]):
        return INTENT_STORY

    # Explain
    if any(k in text for k in ["समजाव", "समजावून", "explain", "कसे", "का"]):
        return INTENT_EXPLAIN

    # Arithmetic
    if any(k in text for k in ARITH_KEYWORDS):
        return INTENT_CALCULATE

    return INTENT_UNKNOWN
