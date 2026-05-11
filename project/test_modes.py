"""Test mode switching and mode-aware intent detection."""
import sys; sys.path.insert(0, ".")
from backend.intent import detect_intent
from backend.quiz import QuizSession

print("=== Mode Switch Intents ===")
cases = [
    ("अंकगणित",           "general",    "mode_arith"),
    ("पायथागोरस मोड",     "general",    "mode_pyth"),
    ("पायथागोरस शिकव",    "general",    "mode_pyth"),
    ("arithmetic",         "general",    "mode_arith"),
]
for text, mode, expected in cases:
    got = detect_intent(text, mode)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' [{mode}] => {got}")

print()
print("=== Pythagoras Mode — all commands resolve to Pythagoras ===")
cases_pyth = [
    ("समजाव",             "pyth_explain"),
    ("गोष्ट सांग",         "pyth_story"),
    ("उदाहरण दे",          "pyth_example"),
    ("क्विझ सुरू कर",      "pyth_quiz"),
    ("3 आणि 4",            "pyth_solve"),
    ("तीन आणि चार",        "pyth_solve"),
    ("शिकव",               "pyth_explain"),
    ("सांगा",              "pyth_explain"),
    ("काय आहे",            "pyth_explain"),
]
for text, expected in cases_pyth:
    got = detect_intent(text, "pythagoras")
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")

print()
print("=== Arithmetic Mode — all commands resolve to arithmetic ===")
cases_arith = [
    ("5 अधिक 3",           "calculate"),
    ("गोष्ट सांग",          "story"),
    ("समजाव",              "explain"),
    ("क्विझ सुरू कर",       "quiz"),
    ("तीन अधिक चार",        "calculate"),
    ("दहा वजा चार",         "calculate"),
]
for text, expected in cases_arith:
    got = detect_intent(text, "arithmetic")
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")

print()
print("=== Quiz Mode Isolation ===")
# Arithmetic mode quiz → no Pythagoras questions
q_arith = QuizSession(total_questions=10, pythagoras_only=False, include_pythagoras=False)
pyth_count = sum(1 for _ in range(10) if q_arith.next_question()["type"] == "pythagoras")
print(f"  [{'PASS' if pyth_count==0 else 'FAIL'}] Arithmetic quiz: {pyth_count}/10 Pythagoras (expected 0)")

# Pythagoras mode quiz → all Pythagoras questions
q_pyth = QuizSession(total_questions=10, pythagoras_only=True)
pyth_count2 = sum(1 for _ in range(10) if q_pyth.next_question()["type"] == "pythagoras")
print(f"  [{'PASS' if pyth_count2==10 else 'FAIL'}] Pythagoras quiz: {pyth_count2}/10 Pythagoras (expected 10)")

print()
print("=== Marathi Number Answers in Quiz ===")
from backend.quiz import QuizSession
q = QuizSession(5, pythagoras_only=True)
q.next_question()
q.current_question = {"question_marathi": "कर्ण किती?", "answer": 5, "type": "pythagoras", "hint": ""}
for ans, expected_correct in [("पाच", True), ("सात", False), ("5", True), ("आठ मिळतो", False)]:
    r = q.check_answer(ans)
    ok = r["correct"] == expected_correct
    print(f"  [{'PASS' if ok else 'FAIL'}] '{ans}' => correct={r['correct']}")

print()
print("All tests done!")
