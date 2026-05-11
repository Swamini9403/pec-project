"""
quiz.py
-------
Dynamic quiz generator for arithmetic + Pythagorean theorem in Marathi.
Generates random questions, accepts spoken answers, tracks score.
"""

import random
import re
import math

# Common Pythagorean triples
PYTH_TRIPLES = [
    (3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17),
    (9, 12, 15), (12, 16, 20), (7, 24, 25), (20, 21, 29),
]


def generate_arithmetic_question() -> dict:
    """Generate a random arithmetic question."""
    operation = random.choice(["add", "sub", "mul", "div"])

    if operation == "add":
        a, b = random.randint(1, 20), random.randint(1, 20)
        answer = a + b
        question = f"{a} आणि {b} यांची बेरीज किती?"

    elif operation == "sub":
        a = random.randint(5, 20)
        b = random.randint(1, a)
        answer = a - b
        question = f"{a} मधून {b} वजा केल्यास किती मिळते?"

    elif operation == "mul":
        a, b = random.randint(1, 10), random.randint(1, 10)
        answer = a * b
        question = f"{a} आणि {b} यांचा गुणाकार किती?"

    else:  # div
        b = random.randint(1, 10)
        answer = random.randint(1, 10)
        a = b * answer
        question = f"{a} ला {b} ने भाग दिल्यास किती मिळते?"

    return {
        "question_marathi": question,
        "answer": answer,
        "type": "arithmetic",
        "operation": operation,
        "a": a, "b": b,
    }


def generate_pythagoras_question() -> dict:
    """Generate a random Pythagorean theorem question."""
    a, b, c = random.choice(PYTH_TRIPLES)
    mode = random.choice(["find_c", "find_a", "find_b"])

    if mode == "find_c":
        question = f"समकोण त्रिकोणात बाजू {a} आणि {b} असल्यास कर्ण किती?"
        answer = c
        hint = f"√({a}² + {b}²) = √{a*a + b*b} = {c}"
    elif mode == "find_a":
        question = f"समकोण त्रिकोणात कर्ण {c} आणि एक बाजू {b} असल्यास दुसरी बाजू किती?"
        answer = a
        hint = f"√({c}² - {b}²) = √{c*c - b*b} = {a}"
    else:
        question = f"समकोण त्रिकोणात कर्ण {c} आणि एक बाजू {a} असल्यास दुसरी बाजू किती?"
        answer = b
        hint = f"√({c}² - {a}²) = √{c*c - a*a} = {b}"

    return {
        "question_marathi": question,
        "answer": answer,
        "type": "pythagoras",
        "hint": hint,
        "a": a, "b": b, "c": c,
    }


def generate_question(include_pythagoras: bool = False, pythagoras_only: bool = False) -> dict:
    """Generate a question based on mode flags."""
    if pythagoras_only:
        return generate_pythagoras_question()
    if include_pythagoras and random.random() < 0.6:
        return generate_pythagoras_question()
    return generate_arithmetic_question()


class QuizSession:
    """Manages a quiz session with score tracking."""

    def __init__(self, total_questions: int = 5, include_pythagoras: bool = False,
                 pythagoras_only: bool = False):
        self.total = total_questions
        self.current = 0
        self.score = 0
        self.current_question = None
        self.include_pythagoras = include_pythagoras
        self.pythagoras_only = pythagoras_only

    def next_question(self) -> dict | None:
        """Get next question. Returns None if quiz is over."""
        if self.current >= self.total:
            return None
        self.current_question = generate_question(self.include_pythagoras, self.pythagoras_only)
        self.current += 1
        return self.current_question

    def check_answer(self, user_answer: str) -> dict:
        """Check user's spoken/typed answer. Accepts digits AND Marathi number words."""
        if self.current_question is None:
            return {"error": "कोणताही प्रश्न नाही."}

        # Convert Marathi number words to digits first
        from backend.math_engine import marathi_words_to_numbers
        converted = marathi_words_to_numbers(user_answer)
        nums = re.findall(r'\d+', converted)

        if not nums:
            return {
                "correct": False,
                "correct_answer": self.current_question["answer"],
                "feedback_marathi": (
                    f"उत्तर समजले नाही. कृपया संख्या सांगा. "
                    f"बरोबर उत्तर {self.current_question['answer']} आहे."
                ),
            }

        given = int(nums[0])
        correct = self.current_question["answer"]

        if given == correct:
            self.score += 1
            feedback = f"शाब्बास! बरोबर उत्तर आहे. {correct} हे योग्य आहे."
        else:
            hint = self.current_question.get("hint", "")
            hint_text = f" ({hint})" if hint else ""
            feedback = f"चुकीचे उत्तर. बरोबर उत्तर {correct} आहे.{hint_text}"

        return {
            "correct": given == correct,
            "correct_answer": correct,
            "feedback_marathi": feedback,
        }

    def final_score(self) -> str:
        """Return Marathi summary of quiz performance."""
        return (
            f"क्विझ संपली! तुम्ही {self.total} पैकी {self.score} प्रश्न बरोबर सोडवले. "
            + ("खूप छान!" if self.score == self.total else
               "चांगले प्रयत्न केले!" if self.score >= self.total // 2 else
               "अजून सराव करा!")
        )
