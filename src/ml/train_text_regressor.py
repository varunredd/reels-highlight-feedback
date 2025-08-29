from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np, evaluate, os, glob, json
from pathlib import Path

MODEL_NAME = "distilbert-base-uncased"
DATA_DIR = "data/datasets"
OUTPUT_DIR = "models/highlight-text-regressor"
REVIEWS_DIR = "notebooks/reviews"   # where feedback is stored


def load_feedback_dataset():
    """Merge all feedback JSONs into a HuggingFace Dataset (if any)."""
    review_files = glob.glob(f"{REVIEWS_DIR}/reviewed_*.json")
    rows = []

    for rf in review_files:
        with open(rf, "r", encoding="utf-8") as f:
            data = json.load(f)
        for clip in data.get("feedback", []):
            rows.append({
                "text": clip["text"],
                "label": float(clip["label"])  # 👍=1, 👎=0
            })

    if rows:
        return Dataset.from_list(rows)
    return None


def main():
    # ---------------------------
    # 1. Load base dataset
    # ---------------------------
    ds = load_dataset("json", data_files={
        "train": f"{DATA_DIR}/train.jsonl",
        "validation": f"{DATA_DIR}/val.jsonl",
    })

    # ---------------------------
    # 2. Load feedback dataset (optional)
    # ---------------------------
    feedback_ds = load_feedback_dataset()
    if feedback_ds:
        print(f"📥 Loaded {len(feedback_ds)} feedback samples")
        # Merge into training split
        ds["train"] = Dataset.from_list(ds["train"][:])  # ensure mutable
        ds["train"] = ds["train"].concatenate(feedback_ds)

    # ---------------------------
    # 3. Tokenization
    # ---------------------------
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(ex):
        return tok(ex["text"], truncation=True, padding="max_length", max_length=256)

    ds = ds.map(tokenize, batched=True)
    ds = ds.rename_column("label", "labels")
    ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    # ---------------------------
    # 4. Model + Training
    # ---------------------------
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=1)

    metric = evaluate.load("spearmanr")

    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        preds = preds.squeeze()
        labels = labels.squeeze()
        return {"spearman": metric.compute(predictions=preds, references=labels)["spearmanr"]}

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="spearman",
        greater_is_better=True,
        fp16=False,
        logging_steps=50,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        tokenizer=tok,
        compute_metrics=compute_metrics
    )

    # ---------------------------
    # 5. Train + Save
    # ---------------------------
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tok.save_pretrained(OUTPUT_DIR)
    print(f"✅ Saved model to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
