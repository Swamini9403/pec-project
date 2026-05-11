import sys
sys.path.insert(0, ".")

from backend.math_engine import solve, detect_operation
from backend.intent import detect_intent

print("=== Operation Detection ===")
cases = [
    ("50 भागिले 10 किती",   "div"),
    ("भागाकार गोष्टीतून सांगा", "div"),
    ("गुणाकार गोष्टीतून सांगा", "mul"),
    ("10 वजा 4",             "sub"),
    ("5 अधिक 3",             "add"),
    ("10 भाग दोन",           "div"),
]
for text, expected in cases:
    got = detect_operation(text)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")

print()
print("=== Intent Detection ===")
intent_cases = [
    ("50 भागिले 10 किती",       "calculate"),
    ("गोष्टीतून सांगा",          "story"),
    ("भागाकार गोष्टीतून सांगा",  "story"),
    ("गुणाकार गोष्टीतून सांगा",  "story"),
    ("समजावून सांगा",            "explain"),
    ("क्विझ सुरू कर",            "quiz"),
    ("परत सांगा",                "repeat"),
]
for text, expected in intent_cases:
    got = detect_intent(text)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] '{text}' => {got}")

print()
print("=== Division Calculation ===")
div_cases = [
    ("50 भागिले 10 किती", 5),
    ("90/90",              1),
    ("10 भाग दोन",        5),
    ("2 भागिले 6",        0.33),
]
for text, expected in div_cases:
    r = solve(text)
    result = r.get("result", r.get("error"))
    ok = abs(float(result) - expected) < 0.01 if isinstance(result, (int,float)) else False
    print(f"  [{'PASS' if ok else 'FAIL'}] '{text}' => {r.get('marathi_result', r.get('error'))}")

print()
print("=== Context-aware story (simulating session) ===")
# Simulate: user says "50 भागिले 10" then "गोष्टीतून सांगा"
from backend.llm_model.llm_inference import story

# Division story with clean numbers
r = story(50, 10, "div")
print(f"  story(50÷10): {r}")

r = story(2, 6, "div")   # non-clean — server fixes a to be divisible
# server would make a = 6*round(2/6) = 6*0=0 → max(1,...) = 6
print(f"  story(2÷6 raw): {r}")

r = story(18, 6, "div")  # clean
print(f"  story(18÷6): {r}")
