import sys
sys.path.insert(0, ".")

from backend.math_engine import solve
from backend.intent import detect_intent
from backend.quiz import QuizSession

# Math engine tests
tests = [
    ("5 + 3 बेरीज", 8),
    ("10 - 4 वजाबाकी", 6),
    ("3 × 4 गुणाकार", 12),
    ("20 ÷ 4 भागाकार", 5),
]
print("=== Math Engine ===")
for text, expected in tests:
    r = solve(text)
    status = "PASS" if r.get("result") == expected else "FAIL"
    print(f"  [{status}] {text} => {r.get('marathi_result', r.get('error'))}")

print()
print("=== Intent Detection ===")
intents = [
    ("5 + 3 किती", "calculate"),
    ("5 + 3 समजावून सांग", "explain"),
    ("गोष्टीतून समजाव", "story"),
    ("क्विझ सुरू कर", "quiz"),
    ("परत सांगा", "repeat"),
]
for text, expected in intents:
    got = detect_intent(text)
    status = "PASS" if got == expected else "FAIL"
    print(f"  [{status}] '{text}' => {got}")

print()
print("=== Quiz Session ===")
q = QuizSession(total_questions=3)
for i in range(3):
    question = q.next_question()
    ans = q.check_answer(str(question["answer"]))
    print(f"  Q{i+1}: {question['question_marathi']} | {ans['feedback_marathi']}")
print(" ", q.final_score())
