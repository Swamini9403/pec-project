import sys; sys.path.insert(0, ".")
from backend.intent import detect_intent
from backend.quiz import QuizSession
from backend.math_engine import marathi_words_to_numbers
from backend.dataset_loader import get_pythagoras_response, reload

print("=== Intent Fixes ===")
cases = [
    ("उदाहरण दे",                                   "pyth_example"),
    ("कर्ण उदाहरण दाखव",                            "pyth_example"),
    ("पायथागोरस गोष्टीतून समजावून सांग",            "pyth_story"),
    ("मला पायथागोरसची क्वीज पाहिजे अंकगणित नको",   "pyth_quiz"),
    ("क्वीज सुरू कर",                                "quiz"),
    ("मला पायथागोरसचे प्रश्न विचारा",               "pyth_quiz"),
    ("पायथागोरस समजाव",                             "pyth_explain"),
    ("त्रिकोण गोष्ट सांग",                           "pyth_story"),
    ("सात",                                          "unknown"),
    ("आठ मिळतो",                                    "unknown"),
    ("मला नाही माहिती आंसर",                         "unknown"),
]
for text, expected in cases:
    got = detect_intent(text)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")

print()
print("=== Marathi Number Answer in Quiz ===")
q = QuizSession(5, pythagoras_only=True)
q.next_question()
q.current_question = {"question_marathi": "कर्ण किती?", "answer": 9, "type": "pythagoras", "hint": ""}

for answer_text, expected_correct in [
    ("सात", False),
    ("नऊ", True),
    ("आठ मिळतो", False),
    ("9", True),
    ("उत्तर आठ आहे", False),
]:
    r = q.check_answer(answer_text)
    ok = r["correct"] == expected_correct
    print(f"  [{'PASS' if ok else 'FAIL'}] '{answer_text}' => correct={r['correct']}, feedback={r['feedback_marathi'][:50]}")

print()
print("=== Dataset Rich Responses ===")
reload()
for mode in ["explain", "story", "example"]:
    resp = get_pythagoras_response(mode)
    length = len(resp)
    ok = length > 100
    print(f"  [{'PASS' if ok else 'FAIL'}] [{mode}] length={length} chars")
    print(f"    {resp[:80]}...")

print()
print("=== Pythagoras-Only Quiz (all 5 must be pythagoras) ===")
q2 = QuizSession(5, pythagoras_only=True)
for i in range(5):
    question = q2.next_question()
    qtype = question.get("type")
    print(f"  [{'PASS' if qtype=='pythagoras' else 'FAIL'}] Q{i+1} [{qtype}]: {question['question_marathi'][:55]}")
