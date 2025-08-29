import gradio as gr
import json, glob, os, subprocess
from pathlib import Path
from datetime import datetime

# Paths
RUNS_DIR = Path("runs")
FEEDBACK_FILE = Path("data/feedback.jsonl")
FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

# Load latest run file
def get_latest_run():
    logs = sorted(glob.glob("runs/*.json"), key=os.path.getmtime, reverse=True)
    if not logs:
        return [], "⚠️ No run found"
    latest = logs[0]
    with open(latest, "r") as f:
        run_data = json.load(f)
    return run_data["clips"], f"Loaded {os.path.basename(latest)}"

clips, status = get_latest_run()

# ---- Helper functions ----
def load_clip(i):
    if i is None:
        i = 0
    if not clips:
        return None, "", "No clips available"
    i = max(0, min(i, len(clips) - 1))
    clip = clips[i]
    return clip["file"], clip["text"], f"Clip {clip['rank']} | Score={clip['score']:.3f}"

def review_clip(i, label):
    if i is None:
        i = 0
    if not clips:
        return "No clips"
    i = max(0, min(i, len(clips) - 1))
    clip = clips[i]
    clip["label"] = label

    # ✅ Save locally
    feedback_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "clip_rank": clip["rank"],
        "clip_file": clip["file"],
        "score": clip["score"],
        "text": clip["text"],
        "label": label,
    }
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")

    # ✅ Push globally to Hugging Face dataset repo
    try:
        subprocess.run(["git", "add", str(FEEDBACK_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", f"Add feedback for clip {clip['rank']}"], check=True)
        subprocess.run(["git", "push", "hf-dataset", "main"], check=True)
    except Exception as e:
        return f"⚠️ Saved locally, but failed to push: {e}"

    return f"✅ Saved feedback for clip {i+1} (label={label})"

# ---- UI ----
with gr.Blocks() as demo:
    gr.Markdown("# 🎬 Highlight Feedback Demo")

    video = gr.Video()
    transcript = gr.Textbox(label="Transcript")
    status_box = gr.Textbox(label="Status", value=status)

    idx = gr.State(0)

    with gr.Row():
        btn_prev = gr.Button("⬅ Prev")
        btn_next = gr.Button("Next ➡")

    with gr.Row():
        btn_good = gr.Button("👍 Good")
        btn_bad = gr.Button("👎 Bad")

    btn_prev.click(lambda i: max(0, (i or 0) - 1), inputs=idx, outputs=idx)\
            .then(load_clip, inputs=idx, outputs=[video, transcript, status_box])
    btn_next.click(lambda i: min(len(clips) - 1, (i or 0) + 1), inputs=idx, outputs=idx)\
            .then(load_clip, inputs=idx, outputs=[video, transcript, status_box])

    btn_good.click(lambda i: review_clip(i, 1), inputs=idx, outputs=status_box)
    btn_bad.click(lambda i: review_clip(i, 0), inputs=idx, outputs=status_box)

    demo.load(fn=load_clip, inputs=idx, outputs=[video, transcript, status_box])

if __name__ == "__main__":
    demo.launch()
