# 🎓 Offline Marathi Voice-Based AI Tutor for Visually Impaired Students

A fully offline voice assistant that teaches arithmetic and the Pythagorean theorem
in Marathi using speech input/output, dataset retrieval, and deterministic math logic.

---

## Project Structure

```
project/
├── backend/
│   ├── app.py              ← Main voice loop (microphone mode)
│   ├── server.py           ← Flask web server (browser/text mode)
│   ├── math_engine.py      ← Arithmetic + Pythagorean theorem solver
│   ├── intent.py           ← Rule-based Marathi intent detection
│   ├── quiz.py             ← Dynamic quiz (arithmetic + Pythagoras)
│   ├── voice.py            ← Vosk STT + pyttsx3 TTS
│   ├── dataset_loader.py   ← Loads both JSONL datasets with fuzzy matching
│   └── llm_model/
│       ├── finetune.py     ← LoRA fine-tuning script (optional)
│       └── llm_inference.py← LLM explanation/story generator
├── dataset/
│   ├── marathi_math_dataset.jsonl
│   └── pythagoras_dataset.jsonl
├── frontend/
│   └── index.html          ← Browser UI with hint tabs
├── vosk_model/             ← Place Vosk model files here
├── requirements.txt
├── test_core.py            ← Arithmetic smoke tests
├── test_bugs.py            ← Regression tests
└── test_pythagoras.py      ← Pythagorean theorem tests
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> On Windows, if `pyaudio` fails: `pip install pipwin && pipwin install pyaudio`

### 2. Download Vosk model (for microphone input)

- Go to: https://alphacephei.com/vosk/models
- Download `vosk-model-small-hi-0.22` (~50MB)
- Extract into `project/vosk_model/`

> Without the model, the app falls back to keyboard input automatically.

---

## Running the App

### Option A — Web UI (recommended)

```bash
python project/backend/server.py
# Open http://localhost:5000
```

### Option B — Voice mode (microphone)

```bash
python project/backend/app.py
```

### Option C — Run tests

```bash
python project/test_core.py
python project/test_bugs.py
python project/test_pythagoras.py
```

---

## Supported Interactions

| User says (Marathi) | Intent | Response |
|---|---|---|
| `पाच अधिक तीन` | calculate | `5 आणि 3 यांची बेरीज 8 आहे.` |
| `10 वजा 4` | calculate | `10 मधून 4 वजा केल्यास 6 मिळते.` |
| `5 + 3 गोष्टीतून समजाव` | story | Story-based explanation |
| `10 - 4 समजावून सांग` | explain | Step-by-step explanation |
| `पायथागोरस समजाव` | pyth_explain | Dataset explanation in Marathi |
| `त्रिकोण गोष्ट सांग` | pyth_story | Story-based Pythagoras explanation |
| `कर्ण उदाहरण दाखव` | pyth_example | Random triple example (3,4,5 etc.) |
| `बाजू 3 आणि 4 असल्यास कर्ण किती` | pyth_solve | `कर्ण = √(9+16) = √25 = 5` |
| `कर्ण 5 आणि बाजू 3 असल्यास बाजू शोधा` | pyth_solve | Missing side calculation |
| `पायथागोरस क्विझ सुरू कर` | pyth_quiz | Mixed Pythagoras + arithmetic quiz |
| `क्विझ सुरू कर` | quiz | Arithmetic-only quiz (5 questions) |
| `परत सांगा` | repeat | Repeats last response |
| `बंद करा` | exit | Goodbye |

---

## Architecture

```
Voice Input (Marathi)
        ↓
  Vosk STT (offline) / Web Speech API (browser)
        ↓
  Intent Detection (rule-based keyword matching)
        ↓
  ┌──────────────────────────────────────────────────┐
  │  calculate    → Math Engine (arithmetic)         │
  │  explain      → LLM / Dataset fallback           │
  │  story        → LLM / Dataset fallback           │
  │  quiz         → Quiz Generator (arithmetic)      │
  │  pyth_explain → Dataset Retrieval (JSONL)        │
  │  pyth_story   → Dataset Retrieval (JSONL)        │
  │  pyth_example → Dynamic Example Generator        │
  │  pyth_solve   → Math Engine (Pythagoras formula) │
  │  pyth_quiz    → Quiz Generator (mixed)           │
  │  repeat       → last_response cache              │
  └──────────────────────────────────────────────────┘
        ↓
  pyttsx3 TTS (offline) / Web Speech Synthesis (browser)
        ↓
  Voice Output (Marathi)
```

---

## Constraints

- Fully offline — no external APIs
- Runs on CPU, lightweight
- Accessible for visually impaired students (large mic button, spacebar trigger, aria-live regions)
