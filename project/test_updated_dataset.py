import sys
sys.path.insert(0, ".")

from backend.llm_model.llm_inference import explain, story
from backend.intent import detect_intent
from backend.math_engine import solve

print("=== Dataset Fallback (new format) ===")

# Test explain
r = explain(5, 3, "add")
print(f"  explain(5+3): {r}")

r = explain(10, 4, "sub")
print(f"  explain(10-4): {r}")

r = explain(4, 9, "mul")
print(f"  explain(4×9): {r}")

r = explain(18, 9, "div")
print(f"  explain(18÷9): {r}")

print()
print("=== Story (new format) ===")

r = story(12, 9, "add")
print(f"  story(12+9): {r}")

r = story(30, 10, "sub")
print(f"  story(30-10): {r}")

r = story(3, 5, "mul")
print(f"  story(3×5): {r}")

r = story(15, 3, "div")
print(f"  story(15÷3): {r}")

print()
print("=== Intent with new-format user speech ===")
cases = [
    ("5 अधिक 3 किती", "calculate"),
    ("5+3 समजाव", "explain"),
    ("12+9 गोष्टीतून समजाव", "story"),
    ("क्विझ सुरू कर", "quiz"),
    ("परत सांगा", "repeat"),
]
for text, expected in cases:
    got = detect_intent(text)
    status = "PASS" if got == expected else "FAIL"
    print(f"  [{status}] '{text}' => {got}")
