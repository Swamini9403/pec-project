"""
server.py
---------
Flask web server for the Offline Marathi Voice-Based AI Tutor.

Modes:
  general    — auto-detect from keywords (default on startup)
  arithmetic — all commands resolve to arithmetic
  pythagoras — all commands resolve to Pythagoras

Run:
    python project/backend/server.py
Open: http://localhost:5000
"""

import sys, os, re, random, math as _math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, send_from_directory
from backend.intent import (
    detect_intent,
    INTENT_MODE_ARITH, INTENT_MODE_PYTH,
    INTENT_CALCULATE, INTENT_EXPLAIN, INTENT_STORY,
    INTENT_QUIZ, INTENT_REPEAT, INTENT_UNKNOWN,
    INTENT_PYTH_EXPLAIN, INTENT_PYTH_STORY,
    INTENT_PYTH_EXAMPLE, INTENT_PYTH_QUIZ, INTENT_PYTH_SOLVE,
)
from backend.math_engine import (
    solve, detect_operation, extract_numbers, marathi_words_to_numbers,
    solve_pythagoras, generate_pythagoras_example,
)
from backend.quiz import QuizSession
from backend.dataset_loader import get_pythagoras_response
from backend.llm_model.llm_inference import explain, story

app = Flask(__name__, static_folder="../frontend")

# ── Session state ──────────────────────────────────────────────────────────────
state = {
    "mode": "general",          # 'general' | 'arithmetic' | 'pythagoras'
    "last_response": "",
    "quiz_session": None,
    "awaiting_quiz_answer": False,
    "last_a": None,
    "last_b": None,
    "last_op": None,
}

MODE_LABELS = {
    "general":    "सामान्य",
    "arithmetic": "अंकगणित",
    "pythagoras": "पायथागोरस",
}


# ── Quiz helpers ───────────────────────────────────────────────────────────────

def _start_quiz(pythagoras_only: bool = False) -> str:
    state["quiz_session"] = QuizSession(
        total_questions=5,
        pythagoras_only=pythagoras_only,
    )
    state["awaiting_quiz_answer"] = False
    q = state["quiz_session"].next_question()
    state["awaiting_quiz_answer"] = True
    label = "पायथागोरस क्विझ" if pythagoras_only else "अंकगणित क्विझ"
    return f"{label} सुरू! प्रश्न 1: {q['question_marathi']}"


def _handle_quiz_answer(text: str) -> str | None:
    """
    If awaiting a quiz answer, process it and return response string.
    Returns None if not in quiz mode.
    """
    s = state
    if not (s["awaiting_quiz_answer"] and s["quiz_session"]):
        return None

    intent = detect_intent(text, s["mode"])

    # ── Quiz stop ──────────────────────────────────────────────────────────
    if any(k in text for k in ["थांब", "बंद", "stop", "क्विझ बंद", "परीक्षा बंद"]):
        s["awaiting_quiz_answer"] = False
        s["quiz_session"] = None
        # Same message might also request a new quiz
        if intent == INTENT_PYTH_QUIZ:
            return _start_quiz(pythagoras_only=True)
        if intent == INTENT_QUIZ:
            return _start_quiz(pythagoras_only=(s["mode"] == "pythagoras"))
        return "क्विझ थांबवली. पुन्हा सुरू करायची असल्यास 'क्विझ सुरू कर' असे सांगा."

    # ── New quiz start mid-quiz → restart ──────────────────────────────────
    if intent == INTENT_PYTH_QUIZ:
        s["awaiting_quiz_answer"] = False
        s["quiz_session"] = None
        return _start_quiz(pythagoras_only=True)
    if intent == INTENT_QUIZ:
        s["awaiting_quiz_answer"] = False
        s["quiz_session"] = None
        return _start_quiz(pythagoras_only=(s["mode"] == "pythagoras"))

    # ── Check if input contains a number ──────────────────────────────────
    converted = marathi_words_to_numbers(text)
    has_number = bool(re.search(r'\d', converted))

    # Non-numeric meaningful command → answer inline, keep quiz alive
    if not has_number and intent not in (INTENT_UNKNOWN, INTENT_REPEAT):
        current_q = s["quiz_session"].current_question
        if intent == INTENT_PYTH_EXPLAIN:
            side = get_pythagoras_response("explain")
        elif intent == INTENT_PYTH_STORY:
            side = get_pythagoras_response("story")
        elif intent == INTENT_PYTH_EXAMPLE:
            side = generate_pythagoras_example()
        else:
            side = "ठीक आहे."
        return f"{side}\n\nक्विझ चालू आहे → {current_q['question_marathi']}"

    # No number at all → repeat question
    if not has_number:
        current_q = s["quiz_session"].current_question
        return f"कृपया फक्त संख्या सांगा.\nप्रश्न पुन्हा: {current_q['question_marathi']}"

    # Has number → check answer
    result = s["quiz_session"].check_answer(converted)
    response = result["feedback_marathi"]
    s["awaiting_quiz_answer"] = False
    q = s["quiz_session"].next_question()
    if q:
        s["awaiting_quiz_answer"] = True
        response += f"\n\nप्रश्न {s['quiz_session'].current}: {q['question_marathi']}"
    else:
        response += "\n\n" + s["quiz_session"].final_score()
    return response


# ── Main router ────────────────────────────────────────────────────────────────

def process_text(text: str) -> str:
    s = state

    # Exit
    if any(k in text for k in ["बंद करा", "exit", "quit"]):
        return "धन्यवाद! पुन्हा भेटू."

    # Quiz answer handling (highest priority after exit)
    quiz_response = _handle_quiz_answer(text)
    if quiz_response is not None:
        s["last_response"] = quiz_response
        return quiz_response

    # Detect intent with current mode context
    intent = detect_intent(text, s["mode"])

    # ── Mode switching ─────────────────────────────────────────────────────
    if intent == INTENT_MODE_ARITH:
        s["mode"] = "arithmetic"
        response = (
            "अंकगणित मोड सुरू! 🔢\n"
            "आता तुम्ही बेरीज, वजाबाकी, गुणाकार, भागाकार शिकू शकता.\n"
            "उदाहरण: 'पाच अधिक तीन', '10 वजा 4', 'क्विझ सुरू कर'"
        )
        s["last_response"] = response
        return response

    if intent == INTENT_MODE_PYTH:
        s["mode"] = "pythagoras"
        response = (
            "पायथागोरस मोड सुरू! 📐\n"
            "आता तुम्ही पायथागोरस प्रमेय शिकू शकता.\n"
            "उदाहरण: 'समजाव', 'गोष्ट सांग', 'उदाहरण दे', 'बाजू 3 आणि 4 कर्ण किती', 'क्विझ सुरू कर'"
        )
        s["last_response"] = response
        return response

    # ── Repeat ────────────────────────────────────────────────────────────
    if intent == INTENT_REPEAT:
        return s["last_response"] or "आधी काहीच सांगितले नाही."

    # ── Pythagoras intents ─────────────────────────────────────────────────
    if intent == INTENT_PYTH_EXPLAIN:
        response = get_pythagoras_response("explain")

    elif intent == INTENT_PYTH_STORY:
        response = get_pythagoras_response("story")

    elif intent == INTENT_PYTH_EXAMPLE:
        response = generate_pythagoras_example()

    elif intent == INTENT_PYTH_QUIZ:
        response = _start_quiz(pythagoras_only=True)

    elif intent == INTENT_PYTH_SOLVE:
        converted = marathi_words_to_numbers(text)
        result = solve_pythagoras(converted)
        response = result.get("marathi_result", result.get("error", "उत्तर काढता आले नाही."))

    # ── Arithmetic intents ─────────────────────────────────────────────────
    elif intent == INTENT_CALCULATE:
        result = solve(text)
        if "error" in result:
            response = result["error"]
        else:
            s["last_a"] = result["a"]
            s["last_b"] = result["b"]
            s["last_op"] = result["operation"]
            response = result["marathi_result"]

    elif intent == INTENT_EXPLAIN:
        text_norm = marathi_words_to_numbers(text)
        nums = extract_numbers(text_norm)
        op = detect_operation(text)
        if len(nums) < 2:
            nums = [s["last_a"], s["last_b"]] if s["last_a"] is not None else []
        if op is None:
            op = s["last_op"]
        if len(nums) < 2 or op is None:
            response = "कृपया आधी एखादे गणित सांगा, मग समजावून सांगतो."
        else:
            a, b = nums[0], nums[1]
            s["last_a"], s["last_b"], s["last_op"] = a, b, op
            response = explain(a, b, op)

    elif intent == INTENT_STORY:
        text_norm = marathi_words_to_numbers(text)
        nums = extract_numbers(text_norm)
        op = detect_operation(text) or s["last_op"] or "add"
        if len(nums) < 2:
            nums = [s["last_a"], s["last_b"]] if s["last_a"] is not None else []
        if len(nums) < 2:
            if op == "div":
                b = random.randint(2, 10); a = b * random.randint(2, 10)
            elif op == "sub":
                a = random.randint(10, 20); b = random.randint(1, a - 1)
            else:
                a, b = random.randint(2, 10), random.randint(2, 10)
            nums = [a, b]
        a, b = nums[0], nums[1]
        if op == "div" and b != 0 and a % b != 0:
            a = b * max(2, _math.ceil(a / b))
        s["last_a"], s["last_b"], s["last_op"] = a, b, op
        response = story(a, b, op)

    elif intent == INTENT_QUIZ:
        # In Pythagoras mode, quiz is always Pythagoras-only
        response = _start_quiz(pythagoras_only=(s["mode"] == "pythagoras"))

    # ── Unknown / fallback ─────────────────────────────────────────────────
    else:
        text_norm = marathi_words_to_numbers(text)
        nums = extract_numbers(text_norm)

        if s["mode"] == "pythagoras" and len(nums) >= 2:
            result = solve_pythagoras(text_norm)
            response = result.get("marathi_result", result.get("error", "उत्तर काढता आले नाही."))
        elif s["mode"] == "arithmetic" and len(nums) >= 2:
            result = solve(text_norm)
            if "error" not in result:
                s["last_a"], s["last_b"], s["last_op"] = result["a"], result["b"], result["operation"]
                response = result["marathi_result"]
            else:
                response = _mode_hint(s["mode"])
        elif len(nums) >= 2 and any(k in text for k in ["कर्ण", "बाजू", "त्रिकोण", "पायथागोरस"]):
            result = solve_pythagoras(text_norm)
            response = result.get("marathi_result", result.get("error", "उत्तर काढता आले नाही."))
        elif len(nums) >= 2:
            result = solve(text_norm)
            if "error" not in result:
                s["last_a"], s["last_b"], s["last_op"] = result["a"], result["b"], result["operation"]
                response = result["marathi_result"]
            else:
                response = _mode_hint(s["mode"])
        else:
            response = _mode_hint(s["mode"])

    s["last_response"] = response
    return response


def _mode_hint(mode: str) -> str:
    if mode == "pythagoras":
        return (
            "पायथागोरस मोड चालू आहे 📐\n"
            "म्हणा: 'समजाव' · 'गोष्ट सांग' · 'उदाहरण दे' · 'बाजू 3 आणि 4 कर्ण किती' · 'क्विझ सुरू कर'\n"
            "अंकगणितासाठी म्हणा: 'अंकगणित'"
        )
    if mode == "arithmetic":
        return (
            "अंकगणित मोड चालू आहे 🔢\n"
            "म्हणा: 'पाच अधिक तीन' · '10 वजा 4' · 'गोष्टीतून समजाव' · 'क्विझ सुरू कर'\n"
            "पायथागोरससाठी म्हणा: 'पायथागोरस मोड'"
        )
    return (
        "मला समजले नाही.\n"
        "अंकगणितासाठी: 'अंकगणित' म्हणा\n"
        "पायथागोरससाठी: 'पायथागोरस मोड' म्हणा"
    )


# ── Flask routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"response": "रिकामा संदेश.", "mode": state["mode"]})
    response = process_text(text)
    return jsonify({"response": response, "mode": state["mode"]})


@app.route("/mode", methods=["GET"])
def get_mode():
    return jsonify({"mode": state["mode"], "label": MODE_LABELS[state["mode"]]})


if __name__ == "__main__":
    print("Starting Marathi Tutor — http://localhost:5000")
    app.run(debug=False, port=5000)
