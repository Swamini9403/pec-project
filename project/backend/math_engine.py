"""
math_engine.py
--------------
Deterministic math engine for:
  - Arithmetic: addition, subtraction, multiplication, division
  - Pythagorean theorem: c = sqrt(a² + b²), find missing sides
100% accurate — no LLM used for calculations.
"""

import re
import math
import random

# ── Marathi number words ───────────────────────────────────────────────────────

MARATHI_WORDS = {
    "शून्य": 0, "एक": 1, "दोन": 2, "तीन": 3, "चार": 4,
    "पाच": 5, "सहा": 6, "सात": 7, "आठ": 8, "नऊ": 9,
    "दहा": 10, "अकरा": 11, "बारा": 12, "तेरा": 13, "चौदा": 14,
    "पंधरा": 15, "सोळा": 16, "सतरा": 17, "अठरा": 18, "एकोणीस": 19,
    "वीस": 20, "तीस": 30, "चाळीस": 40, "पन्नास": 50,
    "साठ": 60, "सत्तर": 70, "ऐंशी": 80, "नव्वद": 90, "शंभर": 100,
}

def marathi_words_to_numbers(text: str) -> str:
    """Replace Marathi number words with digits in the text."""
    for word, digit in MARATHI_WORDS.items():
        text = text.replace(word, str(digit))
    return text

def extract_numbers(text: str) -> list:
    """Extract all integers from text."""
    return [int(n) for n in re.findall(r'\d+', text)]

def detect_operation(text: str) -> str | None:
    """
    Detect math operation from Marathi keywords or symbols.
    Returns: 'add' | 'sub' | 'mul' | 'div' | None
    """
    if any(k in text for k in ["भागाकार", "भागिले", "÷", "/"]):
        return "div"
    if any(k in text for k in ["गुणाकार", "गुणिले", "गुणा", "×", "*"]):
        return "mul"
    if any(k in text for k in ["वजाबाकी", "वजा", "कमी", "minus"]):
        return "sub"
    if any(k in text for k in ["बेरीज", "जोड", "अधिक", "मिळव", "plus", "+"]):
        return "add"
    if "भाग" in text:
        return "div"
    return None

def solve(text: str) -> dict:
    """
    Arithmetic solver. Parses text, detects operation, computes result.
    Returns dict with keys: a, b, operation, result, marathi_result
    """
    text = marathi_words_to_numbers(text)
    numbers = extract_numbers(text)
    operation = detect_operation(text)

    if len(numbers) < 2:
        return {"error": "दोन संख्या सापडल्या नाहीत."}
    if operation is None:
        return {"error": "गणिताचा प्रकार समजला नाही."}

    a, b = numbers[0], numbers[1]

    if operation == "add":
        result = a + b
        expr = f"{a} + {b} = {result}"
        marathi = f"{a} आणि {b} यांची बेरीज {result} आहे."
    elif operation == "sub":
        result = a - b
        expr = f"{a} - {b} = {result}"
        marathi = f"{a} मधून {b} वजा केल्यास {result} मिळते."
    elif operation == "mul":
        result = a * b
        expr = f"{a} × {b} = {result}"
        marathi = f"{a} चा {b} वेळा गुणाकार केल्यास {result} मिळते."
    elif operation == "div":
        if b == 0:
            return {"error": "शून्याने भाग देता येत नाही."}
        result_float = a / b
        result = int(result_float) if result_float == int(result_float) else round(result_float, 2)
        expr = f"{a} ÷ {b} = {result}"
        marathi = f"{a} ला {b} ने भाग दिल्यास {result} मिळते."

    return {
        "a": a, "b": b,
        "operation": operation,
        "result": result,
        "expression": expr,
        "marathi_result": marathi,
    }


# ── Pythagorean Theorem ────────────────────────────────────────────────────────

# Common Pythagorean triples for examples
PYTHAGOREAN_TRIPLES = [
    (3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (7, 24, 25),
    (9, 12, 15), (12, 16, 20), (10, 24, 26), (20, 21, 29), (9, 40, 41),
]

def solve_pythagoras(text: str) -> dict:
    """
    Solve Pythagorean theorem from text.
    Supports:
      - Find hypotenuse (c) given a and b: a² + b² = c²
      - Find missing side given hypotenuse and one side
    Returns dict with: a, b, c, marathi_result
    """
    # Strip quantity/filler words that aren't actual side values
    # e.g. "दोन बाजू तीन आणि चार" → remove "दोन" (means "two sides", not a side value)
    FILLER_WORDS = ["दोन बाजू", "दोन्ही बाजू", "दोन्ही", "बाजू आहेत", "बाजू आहे"]
    clean = text
    for fw in FILLER_WORDS:
        clean = clean.replace(fw, " ")

    # Always convert Marathi words first
    text_norm = marathi_words_to_numbers(clean)
    numbers = extract_numbers(text_norm)

    if len(numbers) < 2:
        return {"error": "कृपया दोन संख्या सांगा. उदाहरण: 'बाजू 3 आणि 4 असल्यास कर्ण किती?'"}

    find_side = any(k in text for k in ["बाजू शोधा", "बाजू काढ", "missing", "दुसरी बाजू"])

    if find_side:
        nums_sorted = sorted(numbers[:2])
        a, c = nums_sorted[0], nums_sorted[1]
        if c <= a:
            return {"error": "कर्ण इतर बाजूपेक्षा मोठा असणे आवश्यक आहे."}
        b_sq = c * c - a * a
        if b_sq < 0:
            return {"error": "दिलेल्या संख्यांनी समकोण त्रिकोण बनत नाही."}
        b = math.sqrt(b_sq)
        b_str = int(b) if b == int(b) else round(b, 2)
        return {
            "a": a, "b": b_str, "c": c,
            "marathi_result": (
                f"जर कर्ण {c} आणि एक बाजू {a} असेल तर "
                f"दुसरी बाजू = √({c}² - {a}²) = √{b_sq} = {b_str} आहे."
            ),
        }
    else:
        a, b = numbers[0], numbers[1]
        c_sq = a * a + b * b
        c = math.sqrt(c_sq)
        c_str = int(c) if c == int(c) else round(c, 2)
        return {
            "a": a, "b": b, "c": c_str,
            "marathi_result": (
                f"पायथागोरस प्रमेयानुसार: {a}² + {b}² = {a*a} + {b*b} = {c_sq}, "
                f"म्हणून कर्ण = √{c_sq} = {c_str} आहे."
            ),
        }


def generate_pythagoras_example() -> str:
    """
    Generate a random Pythagorean example using known triples.
    Returns a Marathi explanation string.
    """
    a, b, c = random.choice(PYTHAGOREAN_TRIPLES)
    templates = [
        f"उदाहरण: जर समकोण त्रिकोणाच्या दोन बाजू {a} आणि {b} असतील, "
        f"तर कर्ण = √({a}² + {b}²) = √({a*a} + {b*b}) = √{a*a + b*b} = {c} येतो.",

        f"समजा एका त्रिकोणाच्या बाजू {a} सेमी आणि {b} सेमी आहेत. "
        f"पायथागोरस प्रमेयानुसार कर्ण = {c} सेमी होतो.",

        f"({a}, {b}, {c}) हे एक प्रसिद्ध पायथागोरस त्रिकूट आहे. "
        f"{a}² + {b}² = {a*a} + {b*b} = {a*a+b*b} = {c}².",
    ]
    return random.choice(templates)
