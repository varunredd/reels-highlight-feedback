"""
Phase 2 - Inference helper for highlight text regressor
Scores subtitle windows with trained Transformer model.
"""

import os, json, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src.ml.make_windows import read_srt, make_windows

MODEL_DIR = "models/highlight-text-regressor"


@torch.no_grad()
def score_windows(srt_path: str, min_len=15.0, max_len=45.0, stride=5.0, top_n=5):
    """Score subtitle windows using trained model, return top-N highlights."""

    if not os.path.isdir(MODEL_DIR):
        raise RuntimeError(f"❌ Model not found at {MODEL_DIR}. Train it first with train_text_regressor.py")

    # Build windows from SRT
    segs = read_srt(srt_path)
    windows = make_windows(segs, min_len=min_len, max_len=max_len, stride=stride)
    texts = [w[2] for w in windows]

    # Load tokenizer + model
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    model.eval()

    # Run batched inference
    scores = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        enc = tok(
            texts[i:i+batch_size],
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt"
        )
        logits = model(**enc).logits.squeeze(-1).cpu().numpy().tolist()
        if isinstance(logits, float):  # single example case
            logits = [logits]
        scores.extend(logits)

    # Pair scores with windows
    scored = [(float(s), *w) for s, w in zip(scores, windows)]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Simple greedy non-overlap filtering
    selected = []
    def overlap(a, b):
        s1, e1 = a[1], a[2]
        s2, e2 = b[1], b[2]
        inter = max(0.0, min(e1, e2) - max(s1, s2))
        union = (e1 - s1) + (e2 - s2) - inter
        return inter / max(1e-6, union)

    for cand in scored:
        if len(selected) >= top_n:
            break
        if all(overlap(cand, sel) <= 0.4 for sel in selected):  # IoU threshold
            selected.append(cand)

    # Helper: seconds → SRT time
    def format_srt_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hrs:02}:{mins:02}:{int(secs):02},{int((secs - int(secs)) * 1000):03}"

    # Format results for pipeline
    results = []
    for idx, (score, s, e, text) in enumerate(selected, start=1):
        times = f"{format_srt_time(s)} --> {format_srt_time(e)}"
        results.append({"rank": idx, "score": score, "times": times, "text": text})

    return results


if __name__ == "__main__":
    out = score_windows("data/transcripts/output.srt")
    print(json.dumps(out, indent=2, ensure_ascii=False))
