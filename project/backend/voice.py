"""
voice.py
--------
Offline voice I/O using:
  - Vosk  → Speech-to-Text (HMM-based acoustic model)
  - pyttsx3 → Text-to-Speech

NOTE: Download a Vosk Marathi model from https://alphacephei.com/vosk/models
      and place it at: project/vosk_model/
      Recommended: vosk-model-small-hi-0.22 (Hindi/Marathi compatible)
      or vosk-model-mr (Marathi specific if available)
"""

import os
import json
import queue
import threading
import pyttsx3

# ── TTS Setup ──────────────────────────────────────────────────────────────────

def _init_tts() -> pyttsx3.Engine:
    """Initialize pyttsx3 engine with best available voice."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)    # speaking speed
    engine.setProperty("volume", 1.0)

    # Try to find a Hindi/Marathi voice (closest available offline)
    voices = engine.getProperty("voices")
    for v in voices:
        if any(lang in v.languages for lang in [b"mr", b"hi", b"mr_IN", b"hi_IN"]):
            engine.setProperty("voice", v.id)
            break

    return engine

_tts_engine = None

def speak(text: str):
    """Convert text to speech and play it."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = _init_tts()
    print(f"[TTS] {text}")
    _tts_engine.say(text)
    _tts_engine.runAndWait()


# ── STT Setup ──────────────────────────────────────────────────────────────────

VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "vosk_model")

def listen(timeout_seconds: int = 7) -> str:
    """
    Record audio from microphone and return recognized text.
    Uses Vosk offline ASR (HMM + DNN acoustic model).
    Falls back to keyboard input if Vosk model is not found.
    """
    # Fallback: if no Vosk model, use keyboard input (useful for testing)
    if not os.path.exists(VOSK_MODEL_PATH):
        print("[WARN] Vosk model not found. Using keyboard input as fallback.")
        return input("तुमचा प्रश्न टाइप करा: ").strip()

    try:
        from vosk import Model, KaldiRecognizer
        import sounddevice as sd

        model = Model(VOSK_MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)

        audio_queue = queue.Queue()
        result_text = [""]
        done_event = threading.Event()

        def audio_callback(indata, frames, time, status):
            audio_queue.put(bytes(indata))

        def process_audio():
            while not done_event.is_set():
                try:
                    data = audio_queue.get(timeout=0.5)
                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        if res.get("text"):
                            result_text[0] = res["text"]
                            done_event.set()
                except queue.Empty:
                    continue

        print("[STT] ऐकत आहे...")
        speak("बोला...")

        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype="int16", channels=1,
                               callback=audio_callback):
            processor = threading.Thread(target=process_audio, daemon=True)
            processor.start()
            done_event.wait(timeout=timeout_seconds)

        final = json.loads(recognizer.FinalResult()).get("text", "")
        return result_text[0] or final or ""

    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        return input("तुमचा प्रश्न टाइप करा: ").strip()
    except Exception as e:
        print(f"[ERROR] STT failed: {e}")
        return input("तुमचा प्रश्न टाइप करा: ").strip()
