"""
test_pythagoras.py
------------------
Tests for Pythagorean theorem support: intent, math engine, quiz, dataset.
"""
import sys
sys.path.insert(0, ".")

from backend.intent import detect_intent
from backend.math_engine import solve_pythagoras, generate_pythagoras_example
from backend.quiz import QuizSession, generate_pythagoras_question
from backend.dataset_loader import get_pythagoras_response

print("=== Pythagoras Intent Detection ===")
cases = [
    ("पायथागोरस समजाव",                    "pyth_explain"),
    ("त्रिकोण गोष्ट सांग",                  "pyth_story"),
    ("कर्ण उदाहरण दाखव",                    "pyth_example"),
    ("पायथागोरस क्विझ सुरू कर",             "pyth_quiz"),
    ("बाजू 3 आणि 4 असल्यास कर्ण किती",     "pyth_solve"),
    ("पायथागोरस",                           "pyth_explain"),
]
for text, expected in cases:
    got = detect_intent(text)
    status = "PASS" if got == expected else "FAIL"
    print(f"  [{status}] '{text}' => {got}")

print()
print("=== Pythagorean Solver ===")
solver_cases = [
    ("बाजू 3 आणि 4 असल्यास कर्ण किती", 5),
    ("5 आणि 12 कर्ण किती",              13),
    ("6 आणि 8 कर्ण किती",               10),
]
for text, expected_c in solver_cases:
    r = solve_pythagoras(text)
    got_c = r.get("c")
    status = "PASS" if got_c == expected_c else "FAIL"
    print(f"  [{status}] '{text}' => c={got_c} | {r.get('marathi_result','')[:60]}")

print()
print("=== Missing Side Solver ===")
r = solve_pythagoras("कर्ण 5 आणि बाजू 3 असल्यास दुसरी बाजू शोधा")
print(f"  Result: {r.get('marathi_result', r.get('error'))}")

print()
print("=== Pythagoras Example Generator ===")
for _ in range(3):
    ex = generate_pythagoras_example()
    print(f"  {ex[:80]}")

print()
print("=== Dataset Loader ===")
for mode in ["explain", "story", "example", "quiz"]:
    resp = get_pythagoras_response(mode)
    print(f"  [{mode}] {resp[:70]}")

print()
print("=== Pythagoras Quiz ===")
q = QuizSession(total_questions=5, include_pythagoras=True)
for i in range(5):
    question = q.next_question()
    ans = q.check_answer(str(question["answer"]))
    qtype = question.get("type", "?")
    print(f"  Q{i+1} [{qtype}]: {question['question_marathi'][:50]} | {ans['feedback_marathi'][:40]}")
print(" ", q.final_score())
