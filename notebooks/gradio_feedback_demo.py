# notebooks/gradio_feedback_demo.py

import gradio as gr
import json
from pathlib import Path

RUNS_DIR = Path("runs")
REVIEWS_DIR = Path("notebooks/reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
LIVE_FEEDBACK_FILE = REVIEWS_DIR / "live_feedback.json"

# Load latest run
logs = sorted(RUNS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
if not logs:
    raise FileNotFoundError("⚠️ No runs found. Run pipeline first to generate clips.")

latest_log = logs[0]
with open(latest_log, "r", encoding="utf-8") as f:
    run_data = json.load(f)

clips = run_data["clips"]

def get_clip(idx):
    if idx < 0 or idx >= len(clips):
        return None, "No more clips."
    clip = clips[idx]
    return clip["file"], f"[Score={clip['score']:.3f}] {clip['text']}"

def review_clip(idx, label):
    clips[idx]["label"] = int(label)
    with open(LIVE_FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(clips, f, indent=2, ensure_ascii=False)
    return f"✅ Saved feedback for clip {idx+1}"

with gr.Blocks() as demo:
    idx = gr.State(0)

    with gr.Row():
        video = gr.Video(label="Clip", autoplay=False)
        transcript = gr.Textbox(label="Transcript", interactive=False)

    with gr.Row():
        btn_prev = gr.Button("⬅️ Previous")
        btn_good = gr.Button("👍 Good")
        btn_bad = gr.Button("👎 Bad")
        btn_next = gr.Button("➡️ Next")

    status = gr.Textbox(label="Status", interactive=False)

    def load_clip(i):
        file, text = get_clip(i)
        return file, text, f"Showing clip {i+1}/{len(clips)}"

    btn_prev.click(lambda i: max(i-1, 0), inputs=idx, outputs=idx).then(
        load_clip, inputs=idx, outputs=[video, transcript, status]
    )
    btn_next.click(lambda i: min(i+1, len(clips)-1), inputs=idx, outputs=idx).then(
        load_clip, inputs=idx, outputs=[video, transcript, status]
    )

    btn_good.click(lambda i: review_clip(i, 1), inputs=idx, outputs=status)
    btn_bad.click(lambda i: review_clip(i, 0), inputs=idx, outputs=status)

    demo.load(load_clip, inputs=idx, outputs=[video, transcript, status])

if __name__ == "__main__":
    demo.launch(share=True)  # share=True gives you a public URL
