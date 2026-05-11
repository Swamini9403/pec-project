"""Simulates the exact failing session to verify all fixes."""
import sys; sys.path.insert(0, ".")

import backend.server as srv

print("=== Simulating exact user session ===\n")

def chat(text):
    r = srv.process_text(text)
    print(f"  USER: {text}")
    print(f"  BOT:  {r[:110]}")
    print()
    return r

# Reset state
srv.state.update({"last_response":"","quiz_session":None,"awaiting_quiz_answer":False,
                  "quiz_is_pythagoras":False,"last_a":None,"last_b":None,"last_op":None})

# Normal interactions
chat("पायथागोरस समजाव")
chat("त्रिकोण गोष्ट सांग")
chat("कर्ण उदाहरण दाखव")
chat("बाजू तीन आणि चार असल्यास कर्ण किती")
chat("बाजू सात आणि 24 असल्यास कर्ण किती")

# Start Pythagoras quiz
r = chat("पायथागोरस क्विझ सुरू करा")
assert "पायथागोरस" in r, "Should say Pythagoras quiz"
assert "समकोण त्रिकोण" in r or "बाजू" in r or "कर्ण" in r, f"Q1 should be Pythagoras, got: {r}"
print("  PASS: Q1 is a Pythagoras question")

# Answer correctly
q1 = srv.state["quiz_session"].current_question
r = chat(str(q1["answer"]))
assert "शाब्बास" in r, "Should be correct"
assert "समकोण त्रिकोण" in r or "बाजू" in r or "कर्ण" in r, f"Q2 should be Pythagoras, got: {r}"
print("  PASS: Q2 is also a Pythagoras question")

# User says something confusing during quiz — should answer AND keep quiz alive
r = chat("हा पायथागोरसचा प्रश्न नाही")
assert "क्विझ चालू आहे" in r or "प्रश्न" in r, f"Should keep quiz alive, got: {r}"
assert srv.state["awaiting_quiz_answer"], "Quiz should still be active"
print("  PASS: Side question answered, quiz kept alive")

# User says Pythagoras quiz again mid-quiz -> restart
r = chat("पायथागोरस क्विझ")
assert "पायथागोरस क्विझ सुरू" in r, f"Should restart quiz, got: {r}"
assert "समकोण त्रिकोण" in r or "बाजू" in r or "कर्ण" in r, f"New Q1 should be Pythagoras, got: {r}"
print("  PASS: Quiz restarted with Pythagoras question")

# Verify all 5 questions are Pythagoras
print("\n=== Verify all 5 questions are Pythagoras ===")
srv.state.update({"quiz_session":None,"awaiting_quiz_answer":False,"quiz_is_pythagoras":False})
chat("पायथागोरस क्विझ सुरू कर")
for i in range(1, 5):
    q = srv.state["quiz_session"].current_question
    qtype = q.get("type","?")
    assert qtype == "pythagoras", f"Q{i} is {qtype}, expected pythagoras!"
    print(f"  PASS: Q{i} [{qtype}]: {q['question_marathi'][:60]}")
    chat(str(q["answer"]))

print("\nAll checks passed!")
