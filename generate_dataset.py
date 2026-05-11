import json
import random

# ===============================
# ➕ ADDITION TEMPLATES (30)
# ===============================

add_explain = [f"{a} + {b} = {{c}} असे होते." for a,b in [(1,1)]]  # placeholder init

add_explain = [
    "{a} आणि {b} एकत्र केल्यास {c} मिळते.",
    "{a} मध्ये {b} मिळवले तर {c} येते.",
    "{a} + {b} = {c} असे होते.",
    "ही बेरीज आहे: {c}.",
    "{a} आणि {b} जोडल्यावर {c} मिळते.",
    "{a} मध्ये {b} घातल्यावर {c} मिळते.",
    "{a} आणि {b} यांची बेरीज म्हणजे {c}.",
    "दोन संख्या {a} आणि {b} मिळून {c} होतात.",
    "{a} + {b} केल्यावर {c} मिळते.",
    "उत्तर {c} आहे कारण {a} आणि {b} जोडले.",
    "{a} आणि {b} मिळून {c} होते.",
    "{a} मध्ये {b} वाढवल्यावर {c} मिळते.",
    "ही गणिताची सोपी बेरीज आहे: {c}.",
    "{a} + {b} = {c}",
    "{a} आणि {b} यांची एकत्रित बेरीज {c} आहे.",
    "{a} आणि {b} मिळवले की {c} होते.",
    "{a} + {b} केल्यास {c} मिळते.",
    "बेरीज केल्यावर उत्तर {c} येते.",
    "{a} मध्ये {b} मिळवून {c} मिळते.",
    "ही बेरीज {c} आहे.",
    "{a} आणि {b} मिळून एकूण {c} झाले.",
    "{a} आणि {b} जोडले तर {c} मिळते.",
    "{a} + {b} = {c}, हे उत्तर आहे.",
    "{a} मध्ये {b} टाकल्यावर {c} मिळते.",
    "{a} आणि {b} एकत्र = {c}",
    "एकूण बेरीज {c} आहे.",
    "{a} आणि {b} मिळून {c} मिळते.",
    "ही बेरीज पूर्ण केल्यावर {c} येते.",
    "{a} + {b} म्हणजे {c}.",
    "{a} आणि {b} मिळून एकूण {c}."
]

add_story = [
    "एका मुलाकडे {a} आंबे होते, त्याला {b} मिळाले, आता {c} झाले.",
    "राहुलकडे {a} पुस्तके होती, त्याने {b} घेतली, आता {c} झाली.",
    "एका टोपलीत {a} सफरचंद होती, {b} टाकली, आता {c} झाली.",
    "एका मुलीकडे {a} चॉकलेट्स होती, तिला {b} मिळाली, आता {c} झाली.",
    "एका वर्गात {a} विद्यार्थी होते, {b} आले, आता {c} झाले.",
] * 6  # makes ~30

# ===============================
# ➖ SUBTRACTION
# ===============================

sub_explain = [
    "{a} मधून {b} वजा केल्यास {c} मिळते.",
    "{a} - {b} = {c}",
    "{a} मधून {b} काढल्यावर {c} उरते.",
    "वजाबाकी केल्यावर {c} मिळते.",
    "{a} मधून {b} कमी केल्यास {c}.",
] * 6

sub_story = [
    "एका मुलाकडे {a} आंबे होते, त्याने {b} खाल्ले, आता {c} उरले.",
    "राहुलकडे {a} पुस्तके होती, त्याने {b} दिली, आता {c} राहिली.",
    "एका टोपलीत {a} सफरचंद होती, {b} काढली, आता {c} उरली.",
    "एका मुलीकडे {a} चॉकलेट्स होती, तिने {b} खाल्ली, आता {c} उरली.",
    "एका बॅगेत {a} पेन्सिल होती, {b} हरवल्या, आता {c} उरल्या.",
] * 6

# ===============================
# ✖️ MULTIPLICATION
# ===============================

mul_explain = [
    "{a} × {b} = {c}",
    "{a} चा {b} वेळा गुणाकार = {c}",
    "{a} ची {b} वेळा बेरीज = {c}",
    "गुणाकार केल्यावर {c} मिळते.",
    "{a} × {b} म्हणजे {c}",
] * 6

mul_story = [
    "एका प्लेटमध्ये {a} लाडू आहेत आणि {b} प्लेट्स आहेत, एकूण {c} लाडू.",
    "एका बॅगेत {a} पुस्तके आहेत आणि {b} बॅगा आहेत, एकूण {c}.",
    "एका वर्गात {a} रांगा आहेत आणि प्रत्येकात {b} विद्यार्थी, एकूण {c}.",
    "एका झाडावर {a} फळे आहेत आणि {b} झाडे, एकूण {c}.",
    "एका बॉक्समध्ये {a} गोळ्या आहेत आणि {b} बॉक्स, एकूण {c}.",
] * 6

# ===============================
# ➗ DIVISION
# ===============================

div_explain = [
    "{a} ÷ {b} = {c}",
    "{a} ला {b} ने भाग = {c}",
    "{a} चे {b} भाग = {c}",
    "भागाकार केल्यावर {c} मिळते.",
    "{a} ला {b} ने वाटल्यास {c}",
] * 6

div_story = [
    "{a} आंबे {b} मुलांमध्ये वाटले, प्रत्येकाला {c}.",
    "{a} चॉकलेट्स {b} मित्रांमध्ये वाटली, प्रत्येकाला {c}.",
    "{a} पुस्तके {b} विद्यार्थ्यांना दिली, प्रत्येकाला {c}.",
    "{a} गोळ्या {b} मुलांना दिल्या, प्रत्येकाला {c}.",
    "{a} फळे {b} लोकांना वाटली, प्रत्येकाला {c}.",
] * 6

# ===============================
# DATA GENERATION
# ===============================

dataset = []

# Addition
for _ in range(300):
    a, b = random.randint(1, 20), random.randint(1, 20)
    c = a + b
    dataset.append({"instruction": f"{a}+{b} समजाव", "response": random.choice(add_explain).format(a=a,b=b,c=c)})
    dataset.append({"instruction": f"{a}+{b} गोष्टीतून समजाव", "response": random.choice(add_story).format(a=a,b=b,c=c)})

# Subtraction
for _ in range(300):
    a = random.randint(5, 30)
    b = random.randint(1, a)
    c = a - b
    dataset.append({"instruction": f"{a}-{b} समजाव", "response": random.choice(sub_explain).format(a=a,b=b,c=c)})
    dataset.append({"instruction": f"{a}-{b} गोष्टीतून समजाव", "response": random.choice(sub_story).format(a=a,b=b,c=c)})

# Multiplication
for _ in range(300):
    a, b = random.randint(1, 12), random.randint(1, 12)
    c = a * b
    dataset.append({"instruction": f"{a}×{b} समजाव", "response": random.choice(mul_explain).format(a=a,b=b,c=c)})
    dataset.append({"instruction": f"{a}×{b} गोष्टीतून समजाव", "response": random.choice(mul_story).format(a=a,b=b,c=c)})

# Division
for _ in range(300):
    b = random.randint(1, 12)
    c = random.randint(1, 12)
    a = b * c
    dataset.append({"instruction": f"{a}÷{b} समजाव", "response": random.choice(div_explain).format(a=a,b=b,c=c)})
    dataset.append({"instruction": f"{a}÷{b} गोष्टीतून समजाव", "response": random.choice(div_story).format(a=a,b=b,c=c)})

random.shuffle(dataset)

with open("marathi_math_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ Dataset generated with {len(dataset)} samples!")