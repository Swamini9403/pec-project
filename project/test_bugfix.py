import sys; sys.path.insert(0, ".")
from backend.intent import detect_intent
from backend.math_engine import solve_pythagoras, marathi_words_to_numbers

print("=== Bug Fix Verification ===")

cases = [
    ("बाजू तीन आणि चार असल्यास कर्ण किती",  "pyth_solve"),
    ("दोन बाजू तीन आणि चार कर्ण काढा",       "pyth_solve"),
    ("दोन बाजू आहेत तीन आणि चार कर्ण काढा",  "pyth_solve"),
    ("कोणता नियम",                             "pyth_explain"),
    ("क्विक सुरू करा",                         "quiz"),
    ("परीक्षा घ्या",                            "quiz"),
    ("पायथागोरस ची परीक्षा घ्या",              "pyth_quiz"),
    ("कर्ण उदाहरण दाखव",                       "pyth_example"),
    ("पायथागोरसचे प्रमेय सांगा",               "pyth_explain"),
    ("बाजू 3 आणि 4 असल्यास कर्ण किती",        "pyth_solve"),
]
for text, expected in cases:
    got = detect_intent(text)
    print(f"  [{'PASS' if got==expected else 'FAIL'}] \"{text}\" => {got}")

print()
print("=== Marathi Word Solve ===")
for text in [
    "बाजू तीन आणि चार असल्यास कर्ण किती",
    "दोन बाजू तीन आणि चार",
    "बाजू 3 आणि 4 असल्यास कर्ण किती",
]:
    converted = marathi_words_to_numbers(text)
    r = solve_pythagoras(converted)
    print(f"  \"{text}\"")
    print(f"    => {r.get('marathi_result', r.get('error'))}")

print()
print("=== Quiz Stop (server simulation) ===")
# Simulate the quiz-stop logic from server
stop_words = ["थांब", "बंद", "stop", "क्विझ बंद", "परीक्षा बंद"]
for text in ["परीक्षा थांबा", "क्विझ बंद करा", "थांब"]:
    hit = any(k in text for k in stop_words)
    print(f"  [{'PASS' if hit else 'FAIL'}] \"{text}\" => stop={hit}")
