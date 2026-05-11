"""
finetune.py
-----------
Fine-tunes a small LLM (TinyLlama) on the Marathi math dataset using
HuggingFace Transformers + PEFT (LoRA) for low-resource systems.

Usage:
    python finetune.py

Output:
    Saves fine-tuned adapter to: project/backend/llm_model/marathi_tutor_lora/
"""

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType

# ── Config ─────────────────────────────────────────────────────────────────────

BASE_MODEL   = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"   # ~600MB, runs on CPU/low GPU
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/marathi_math_dataset.jsonl")
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "marathi_tutor_lora")
MAX_LENGTH   = 128
EPOCHS       = 3
BATCH_SIZE   = 4

# ── Load Dataset ───────────────────────────────────────────────────────────────

def load_jsonl(path: str) -> list[dict]:
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

def format_prompt(sample: dict) -> str:
    """Format instruction-response pair into a single training string."""
    return f"### Instruction:\n{sample['instruction']}\n\n### Response:\n{sample['response']}"

# ── Tokenize ───────────────────────────────────────────────────────────────────

def tokenize(batch, tokenizer):
    texts = [format_prompt({"instruction": i, "response": r})
             for i, r in zip(batch["instruction"], batch["response"])]
    tokens = tokenizer(
        texts,
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Loading dataset...")
    raw = load_jsonl(DATASET_PATH)
    dataset = Dataset.from_list(raw)
    print(f"  {len(dataset)} samples loaded.")

    print(f"Loading base model: {BASE_MODEL}")

    # Use 4-bit quantization if GPU available, else plain CPU
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=bnb_config,
            device_map="auto",
        )
    else:
        print("  No GPU found — loading in float32 on CPU (slower but works).")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    # LoRA config — only trains ~0.1% of parameters
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,                    # rank
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],  # attention layers
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("Tokenizing dataset...")
    tokenized = dataset.map(
        lambda b: tokenize(b, tokenizer),
        batched=True,
        remove_columns=dataset.column_names,
    )

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        logging_steps=20,
        save_strategy="epoch",
        fp16=use_gpu,
        report_to="none",
        dataloader_pin_memory=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("Starting fine-tuning...")
    trainer.train()

    print(f"Saving LoRA adapter to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Fine-tuning complete!")


if __name__ == "__main__":
    main()
