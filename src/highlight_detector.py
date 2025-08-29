"""
Phase 2 - Highlight Detector

- Preferred: Transformer model (text regressor) to rank highlight-worthy windows.
- Fallback: Simple keyword-based scoring if model not trained.
"""

import os
import re
import random
from src.ml.infer_text_regressor import score_windows

MODEL_DIR = "models/highlight-text-regressor"


def _format_tuple_list(model_results):
    """Convert model results to (score, idx, times, text)."""
    out = []
    for i, r in enumerate(model_results, start=1):
        out.append((float(r["score"]), str(i), r["times"], r["text"]))
    return out


def extract_highlights(srt_file: str, top_n: int = 5):
    """
    Extract top N highlight-worthy segments.
    Preferred: Transformer model, with exploration sampling.
    Falls back to keyword-based scoring if model not available.
    """
    if os.path.isdir(MODEL_DIR):
        try:
            # Get more candidates (e.g. top 30)
            results = score_windows(
                srt_file,
                min_len=15.0,
                max_len=45.0,
                stride=5.0,
                top_n=30
            )

            if not results:
                raise RuntimeError("score_windows returned empty results")

            # Always keep best 3
            stable = results[:min(3, len(results))]

            # Randomly sample the rest from ranks 4–20
            pool = results[3:20]
            exploratory = []
            if pool and len(stable) < top_n:
                exploratory = random.sample(
                    pool, k=min(top_n - len(stable), len(pool))
                )

            selected = stable + exploratory
            return [(r["score"], r["rank"], r["times"], r["text"]) for r in selected]

        except Exception as e:
            print(f"⚠️ Model inference failed, falling back to keywords. Error: {e}")

    # ----------------------------
    # Fallback: keyword-based scoring
    # ----------------------------
    HIGHLIGHT_KEYWORDS = [
        "amazing", "important", "secret",
        "wow", "never", "always", "hack"
    ]

    def score_segment(text: str) -> int:
        """Count keyword matches in the text."""
        text_lower = text.lower()
        return sum(1 for kw in HIGHLIGHT_KEYWORDS if re.search(rf"\b{kw}\b", text_lower))

    highlights = []
    with open(srt_file, "r", encoding="utf-8") as f:
        content = f.read().strip().split("\n\n")

    for block in content:
        lines = block.split("\n")
        if len(lines) >= 3:
            idx, times, text = lines[0], lines[1], " ".join(lines[2:])
            score = score_segment(text)
            if score > 0:
                highlights.append((float(score), idx, times, text))

    highlights.sort(key=lambda x: x[0], reverse=True)
    return highlights[:top_n]


if __name__ == "__main__":
    results = extract_highlights("data/transcripts/sample.srt")
    for score, idx, times, text in results:
        print(f"[{times}] {text} (score={score:.3f})")
