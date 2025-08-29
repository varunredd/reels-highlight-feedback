# src/ml/build_feedback_dataset.py

import json, glob
from pathlib import Path

REVIEWS_DIR = Path("notebooks/reviews")
OUTPUT_FILE = Path("data/feedback.jsonl")

def main():
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(str(REVIEWS_DIR / "reviewed_*.json")))
    if not files:
        print("⚠️ No review files found.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                feedback = data.get("feedback", [])
                for clip in feedback:
                    # each line = one training sample
                    record = {
                        "text": clip["text"],
                        "label": clip["label"],  # 1=good, 0=bad
                        "score": clip["score"],
                        "times": clip["times"],
                        "file": clip["file"],
                        "source_review": fpath,
                    }
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Built feedback dataset: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
