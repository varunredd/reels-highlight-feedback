import json, os, random
from pathlib import Path

# Reuse SRT helpers like in your subtitle_utils, re-implement quickly here:
def parse_srt_time(s):
    h, m, s_ms = s.split(":")
    sec, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000.0

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02},{int((secs - int(secs))*1000):03}"

def read_srt(path):
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")
    segs = []
    for b in blocks:
        lines = b.split("\n")
        if len(lines) >= 3:
            times = lines[1]
            s, e = times.split(" --> ")
            text = " ".join(lines[2:]).strip()
            segs.append((parse_srt_time(s), parse_srt_time(e), text))
    return segs

def make_windows(segments, min_len=15.0, max_len=45.0, stride=5.0):
    """
    Slide over timeline with fixed stride; window text = concat segments overlapping [t0, t1].
    Returns list of (start_sec, end_sec, text)
    """
    if not segments: return []
    total_end = segments[-1][1]
    t = 0.0
    out = []
    while t < total_end:
        t0, t1 = t, min(t + max_len, total_end)
        # collect segs overlapping window and build text
        texts = []
        last_end = t0
        for (s, e, txt) in segments:
            if e < t0: continue
            if s > t1: break
            texts.append(txt)
            last_end = max(last_end, e)
        if texts:
            # window must be at least min_len long; if too short, extend to last_end if possible
            real_end = max(t0 + min_len, min(last_end, t1))
            out.append((t0, real_end, " ".join(texts)))
        t += stride
    return out

from src.ml.heuristics import score_text

def main(in_srt="data/transcripts/output.srt",
         out_dir="data/datasets",
         train_name="train.jsonl",
         val_name="val.jsonl",
         min_len=15.0, max_len=45.0, stride=5.0,
         val_ratio=0.1, seed=42):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    segs = read_srt(in_srt)
    windows = make_windows(segs, min_len=min_len, max_len=max_len, stride=stride)

    # pseudo-label
    samples = []
    for (s, e, text) in windows:
        label = score_text(text)
        samples.append({
            "start": s, "end": e,
            "text": text, "label": float(label)
        })

    random.Random(seed).shuffle(samples)
    n_val = max(1, int(len(samples)*val_ratio))
    val = samples[:n_val]
    train = samples[n_val:]

    def write_jsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")

    write_jsonl(os.path.join(out_dir, train_name), train)
    write_jsonl(os.path.join(out_dir, val_name), val)
    print(f"✅ Wrote {len(train)} train and {len(val)} val to {out_dir}")

if __name__ == "__main__":
    main()
