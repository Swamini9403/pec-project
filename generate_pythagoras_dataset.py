import json
import random

dataset = []

# ===============================
# 📘 EXPLANATION (DETAILED)
# ===============================
explanations = [
    """पायथागोरस प्रमेय समकोण त्रिकोणासाठी वापरला जातो.
जर त्रिकोणात एक कोन 90 अंशाचा असेल, तर:
कर्ण² = बाजू1² + बाजू2²

उदाहरण:
3² + 4² = 9 + 16 = 25
म्हणून कर्ण = 5""",

    """समकोण त्रिकोणात सर्वात मोठी बाजू कर्ण असते.
कर्ण काढण्यासाठी:
a² + b² = c² हा नियम वापरतात.

उदाहरण:
5² + 12² = 25 + 144 = 169
कर्ण = 13"""
] * 15  # 30 samples

# ===============================
# 📖 STORY (FIXED - STRUCTURED)
# ===============================
def generate_story():
    triples = [(3,4,5), (5,12,13), (6,8,10)]
    a,b,c = random.choice(triples)

    return f"""
एका मुलाला भिंतीच्या टोकापर्यंत पोहोचायचे होते.

तो सरळ वर चढू शकत नाही, म्हणून तो तिरका मार्ग वापरतो.

भिंतीची उंची {a} मीटर आहे.
जमिनीवरचे अंतर {b} मीटर आहे.

पायथागोरस प्रमेयानुसार:
{a}² + {b}² = {c}²

म्हणून कर्ण = {c} मीटर.

यामुळे त्याला सोपा मार्ग मिळाला.
"""

for _ in range(30):
    dataset.append({
        "instruction": "गोष्ट वापरून पायथागोरस समजाव",
        "response": generate_story()
    })

# ===============================
# 🧮 EXAMPLES (CLEAR)
# ===============================
triples = [
    (3,4,5),(5,12,13),(6,8,10),(8,15,17),(7,24,25),
    (9,12,15),(12,16,20),(10,24,26),(20,21,29),(12,35,37),
    (9,40,41),(28,45,53),(11,60,61),(16,63,65),(33,56,65),
    (48,55,73),(13,84,85),(36,77,85),(39,80,89),(65,72,97),
    (20,15,25),(18,24,30),(14,48,50),(27,36,45),(30,40,50),
    (24,45,51),(12,9,15),(8,6,10),(15,20,25),(7,24,25)
]

for a,b,c in triples:
    dataset.append({
        "instruction": "उदाहरण दे",
        "response": f"""
जर बाजू {a} आणि {b} असतील:

Step 1: {a}² = {a*a}
Step 2: {b}² = {b*b}
Step 3: बेरीज = {a*a + b*b}
Step 4: √ = {c}

म्हणून कर्ण = {c}
"""
    })

# ===============================
# 🎮 QUIZ (ONLY PYTHAGORAS)
# ===============================
quiz_templates = [
    "जर बाजू {a} आणि {b} असतील तर कर्ण किती?",
    "समकोण त्रिकोणात {a} आणि {b} दिले आहेत, कर्ण काढा.",
    "{a} आणि {b} असल्यास कर्ण काय येईल?"
]

for _ in range(30):
    a,b,c = random.choice(triples)
    dataset.append({
        "instruction": "पायथागोरस quiz दे",
        "response": random.choice(quiz_templates).format(a=a,b=b)
    })

# ===============================
# EXPLANATION ADD
# ===============================
for text in explanations:
    dataset.append({
        "instruction": "पायथागोरस समजाव",
        "response": text
    })

# Shuffle
random.shuffle(dataset)

# Save
with open("pythagoras_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ Dataset generated with {len(dataset)} samples!")