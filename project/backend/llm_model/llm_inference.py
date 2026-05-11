"""
llm_inference.py
----------------
Loads the fine-tuned LoRA model and generates Marathi explanations/stories.
Used ONLY for: explanation and storytelling.
NOT used for: calculations or quiz generation.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

BASE_MODEL  = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_PATH   = os.path.join(os.path.dirname(__file__), "marathi_tutor_lora")
FALLBACK_PATH = os.path.join(os.path.dirname(__file__),
                             "../../dataset/marathi_math_dataset.jsonl")
PYTH_FALLBACK_PATH = os.path.join(os.path.dirname(__file__),
                                  "../../dataset/pythagoras_dataset.jsonl")

# ── Fallback: dataset lookup (no model needed) ─────────────────────────────────

import json
import difflib

def _load_fallback_dataset(path: str) -> list[dict]:
    data = []
    if not os.path.exists(path):
        return data
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

_fallback_data = None

def _fallback_response(instruction: str) -> str:
    """
    Find best matching response from dataset.
    Strategy:
      1. Exact match
      2. Same operation + same numbers (different spacing)
      3. Same operation type — substitute actual numbers into the response template
    """
    global _fallback_data
    if _fallback_data is None:
        _fallback_data = _load_fallback_dataset(FALLBACK_PATH)

    if not _fallback_data:
        return "माफ करा, मला उत्तर सापडले नाही."

    import re, random

    # Exact match
    for d in _fallback_data:
        if d["instruction"] == instruction:
            return d["response"]

    # Extract numbers and operation type from the query instruction
    # e.g. "5+3 समजाव" → nums=[5,3], op="+", mode="समजाव"
    query_nums = re.findall(r'\d+', instruction)
    op_char = None
    for ch in ["+", "-", "×", "÷"]:
        if ch in instruction:
            op_char = ch
            break

    mode = "गोष्टीतून" if "गोष्टीतून" in instruction else "समजाव"

    if op_char and len(query_nums) >= 2:
        a, b = int(query_nums[0]), int(query_nums[1])

        # Find a dataset entry with same op + same mode, then substitute numbers
        candidates = [
            d for d in _fallback_data
            if op_char in d["instruction"] and mode in d["instruction"]
        ]

        if candidates:
            template_entry = random.choice(candidates)
            response = template_entry["response"]

            # Replace the numbers in the response with the actual a, b, result
            op_map = {"+": lambda x,y: x+y, "-": lambda x,y: x-y,
                      "×": lambda x,y: x*y, "÷": lambda x,y: x//y}
            result = op_map[op_char](a, b)

            # Get the original numbers from the template to replace them
            orig_nums = re.findall(r'\d+', template_entry["instruction"])
            if len(orig_nums) >= 2:
                oa, ob = int(orig_nums[0]), int(orig_nums[1])
                orig_result = op_map[op_char](oa, ob)
                # Replace in descending order of number length to avoid partial replacements
                replacements = [
                    (str(orig_result), str(result)),
                    (str(oa), str(a)),
                    (str(ob), str(b)),
                ]
                # Sort by length descending so longer numbers replaced first
                replacements.sort(key=lambda x: len(x[0]), reverse=True)
                for old, new in replacements:
                    response = response.replace(old, new)

            return response

    # Last resort: fuzzy match
    instructions = [d["instruction"] for d in _fallback_data]
    matches = difflib.get_close_matches(instruction, instructions, n=1, cutoff=0.4)
    if matches:
        for d in _fallback_data:
            if d["instruction"] == matches[0]:
                return d["response"]

    return random.choice(_fallback_data)["response"]


# ── LLM Inference ──────────────────────────────────────────────────────────────

class MarathiTutor:
    """
    Wraps the fine-tuned LLM for explanation and storytelling.
    Falls back to dataset lookup if model is not yet trained.
    """

    def __init__(self):
        self.pipe = None
        self._try_load_model()

    def _try_load_model(self):
        """Load fine-tuned model if available."""
        if not os.path.exists(LORA_PATH):
            print("[LLM] Fine-tuned model not found. Using dataset fallback.")
            return

        try:
            print("[LLM] Loading fine-tuned model...")
            tokenizer = AutoTokenizer.from_pretrained(LORA_PATH)
            base = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
            )
            model = PeftModel.from_pretrained(base, LORA_PATH)
            model.eval()

            self.pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=80,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
            print("[LLM] Model loaded successfully.")
        except Exception as e:
            print(f"[LLM] Could not load model: {e}. Using dataset fallback.")
            self.pipe = None

    def generate(self, instruction: str) -> str:
        """Generate a Marathi response for the given instruction."""
        if self.pipe is None:
            return _fallback_response(instruction)

        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
        try:
            output = self.pipe(prompt)[0]["generated_text"]
            # Extract only the response part
            if "### Response:" in output:
                return output.split("### Response:")[-1].strip()
            return output.strip()
        except Exception as e:
            print(f"[LLM] Generation error: {e}")
            return _fallback_response(instruction)


# Singleton instance
_tutor = None

def get_tutor() -> MarathiTutor:
    global _tutor
    if _tutor is None:
        _tutor = MarathiTutor()
    return _tutor


def explain(a: int, b: int, operation: str) -> str:
    """Generate explanation for a math operation."""
    op_map = {"add": "+", "sub": "-", "mul": "×", "div": "÷"}
    symbol = op_map.get(operation, "+")
    # Match new dataset format: "5+3 समजाव" (no spaces around operator)
    instruction = f"{a}{symbol}{b} समजाव"
    return get_tutor().generate(instruction)


def story(a: int, b: int, operation: str) -> str:
    """Generate a story-based explanation."""
    op_map = {"add": "+", "sub": "-", "mul": "×", "div": "÷"}
    symbol = op_map.get(operation, "+")
    # Match new dataset format: "5+3 गोष्टीतून समजाव"
    instruction = f"{a}{symbol}{b} गोष्टीतून समजाव"
    return get_tutor().generate(instruction)
