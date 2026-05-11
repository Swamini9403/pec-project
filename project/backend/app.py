"""
app.py
------
Main entry point for the Offline Marathi Voice-Based AI Tutor.

Architecture:
  Voice Input → STT (Vosk) → Intent Detection → Router
      → Math Engine (arithmetic + Pythagoras)
      → Dataset Retrieval (JSONL)
      → Quiz Generator
  → TTS (pyttsx3) → Voice Output

Run:
    python project/backend/app.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.voice import speak, listen
from backend.intent import (
    detect_intent,
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

# ── State ──────────────────────────────────────────────────────────────────────

last_response: str = ""
quiz_session: QuizSession = None
awaiting_quiz_answer: bool = False

# ── Helpers ────────────────────────────────────────────────────────────────────

def respond(text: str):
    global last_response
    last_response = text
    speak(text)


def handle_calculate(text: str):
    result = solve(text)
    respond(result.get("marathi_result", result.get("error", "उत्तर काढता आले नाही.")))


def handle_explain(text: str):
    text_norm = marathi_words_to_numbers(text)
    nums = extract_numbers(text_norm)
    op = detect_operation(text)
    if len(nums) < 2 or op is None:
        respond("कृपया दोन संख्या आणि गणिताचा प्रकार सांगा.")
        return
    respond(explain(nums[0], nums[1], op))


def handle_story(text: str):
    import random
    text_norm = marathi_words_to_numbers(text)
    nums = extract_numbers(text_norm)
    op = detect_operation(text) or "add"
    if len(nums) < 2:
        a, b = random.randint(1, 10), random.randint(1, 10)
        nums = [a, b]
    respond(story(nums[0], nums[1], op))


def handle_quiz(include_pythagoras: bool = False):
    global quiz_session, awaiting_quiz_answer
    quiz_session = QuizSession(total_questions=5, include_pythagoras=include_pythagoras)
    awaiting_quiz_answer = False
    label = "पायथागोरस क्विझ" if include_pythagoras else "क्विझ"
    respond(f"{label} सुरू होत आहे! मी प्रश्न विचारतो, तुम्ही उत्तर सांगा.")
    ask_next_quiz_question()


def ask_next_quiz_question():
    global awaiting_quiz_answer
    if quiz_session is None:
        return
    q = quiz_session.next_question()
    if q is None:
        respond(quiz_session.final_score())
        return
    awaiting_quiz_answer = True
    respond(f"प्रश्न {quiz_session.current}: {q['question_marathi']}")


def handle_quiz_answer(text: str):
    global awaiting_quiz_answer
    if quiz_session is None:
        return
    result = quiz_session.check_answer(text)
    respond(result["feedback_marathi"])
    awaiting_quiz_answer = False
    ask_next_quiz_question()


# ── Main Loop ──────────────────────────────────────────────────────────────────

def main():
    speak("नमस्कार! मी तुमचा मराठी गणित शिक्षक आहे. अंकगणित आणि पायथागोरस प्रमेय शिकूया!")

    while True:
        text = listen()

        if not text:
            speak("मला समजले नाही. कृपया पुन्हा सांगा.")
            continue

        print(f"[USER] {text}")

        if any(k in text for k in ["बंद करा", "exit", "quit", "थांब"]):
            speak("धन्यवाद! पुन्हा भेटू.")
            break

        if awaiting_quiz_answer:
            handle_quiz_answer(text)
            continue

        intent = detect_intent(text)
        print(f"[INTENT] {intent}")

        if intent == INTENT_REPEAT:
            speak(last_response) if last_response else speak("आधी काहीच सांगितले नाही.")

        elif intent == INTENT_CALCULATE:
            handle_calculate(text)

        elif intent == INTENT_EXPLAIN:
            handle_explain(text)

        elif intent == INTENT_STORY:
            handle_story(text)

        elif intent == INTENT_QUIZ:
            handle_quiz(include_pythagoras=False)

        elif intent == INTENT_PYTH_EXPLAIN:
            respond(get_pythagoras_response("explain"))

        elif intent == INTENT_PYTH_STORY:
            respond(get_pythagoras_response("story"))

        elif intent == INTENT_PYTH_EXAMPLE:
            respond(generate_pythagoras_example())

        elif intent == INTENT_PYTH_QUIZ:
            handle_quiz(include_pythagoras=True)

        elif intent == INTENT_PYTH_SOLVE:
            result = solve_pythagoras(text)
            respond(result.get("marathi_result", result.get("error", "उत्तर काढता आले नाही.")))

        else:
            speak(
                "मला समजले नाही. उदाहरण: 'पाच अधिक तीन', "
                "'पायथागोरस समजाव', 'बाजू 3 आणि 4 असल्यास कर्ण किती', 'क्विझ सुरू कर'"
            )


if __name__ == "__main__":
    main()
