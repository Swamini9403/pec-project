import sys; sys.path.insert(0, ".")
from backend.quiz import QuizSession, generate_pythagoras_question

print("=== Pythagoras-Only Quiz (all 5 questions must be pythagoras) ===")
q = QuizSession(total_questions=5, pythagoras_only=True)
all_pyth = True
for i in range(5):
    question = q.next_question()
    qtype = question.get("type")
    status = "PASS" if qtype == "pythagoras" else "FAIL"
    if qtype != "pythagoras":
        all_pyth = False
    print(f"  [{status}] Q{i+1} [{qtype}]: {question['question_marathi'][:60]}")
print(f"  All Pythagoras: {'YES' if all_pyth else 'NO'}")

print()
print("=== Mixed Quiz (arithmetic + pythagoras, ~70% pyth) ===")
q2 = QuizSession(total_questions=10, include_pythagoras=True)
pyth_count = 0
for i in range(10):
    question = q2.next_question()
    if question.get("type") == "pythagoras":
        pyth_count += 1
print(f"  Pythagoras questions: {pyth_count}/10 (expected ~7)")

print()
print("=== Stop + Restart in same sentence ===")
# Simulate server logic
import sys; sys.path.insert(0, ".")
from backend.intent import detect_intent, INTENT_PYTH_QUIZ, INTENT_QUIZ

cases = [
    ("परीक्षा थांबा मला पायथागोरसची क्वीज पाहिजे", INTENT_PYTH_QUIZ),
    ("थांब आणि नवीन क्विझ सुरू कर",                INTENT_QUIZ),
    ("क्विझ बंद कर पायथागोरस परीक्षा घे",          INTENT_PYTH_QUIZ),
]
for text, expected in cases:
    got = detect_intent(text)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")
