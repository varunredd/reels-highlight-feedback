import gradio as gr
import json, glob, os
from pathlib import Path

# Load latest run file
def get_latest_run():
    logs = sorted(glob.glob("runs/*.json"), key=os.path.getmtime, reverse=True)
    if not logs:
        return [], "No run found"
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
    clips[i]["label"] = label
    return f"Saved feedback for clip {i+1}"

# ---- UI ----
with gr.Blocks() as demo:
    gr.Markdown("# 🎬 Highlight Feedback Demo")

    video = gr.Video()
    transcript = gr.Textbox(label="Transcript")
    status_box = gr.Textbox(label="Status", value=status)

    # ✅ State must be defined inside Blocks
    idx = gr.State(0)  # initial index

    with gr.Row():
        btn_prev = gr.Button("⬅ Prev")
        btn_next = gr.Button("Next ➡")

    with gr.Row():
        btn_good = gr.Button("👍 Good")
        btn_bad = gr.Button("👎 Bad")

    # Navigation
    btn_prev.click(lambda i: max(0, (i or 0) - 1), inputs=idx, outputs=idx)\
            .then(load_clip, inputs=idx, outputs=[video, transcript, status_box])
    btn_next.click(lambda i: min(len(clips) - 1, (i or 0) + 1), inputs=idx, outputs=idx)\
            .then(load_clip, inputs=idx, outputs=[video, transcript, status_box])

    # Feedback
    btn_good.click(lambda i: review_clip(i, 1), inputs=idx, outputs=status_box)
    btn_bad.click(lambda i: review_clip(i, 0), inputs=idx, outputs=status_box)

    # Initialize on load
    demo.load(fn=load_clip, inputs=idx, outputs=[video, transcript, status_box])

if __name__ == "__main__":
    demo.launch()
