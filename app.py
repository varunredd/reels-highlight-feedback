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
idx = gr.State(0)

def load_clip(i):
    if not clips: return None, "", "No clips available"
    clip = clips[i]
    return clip["file"], clip["text"], f"Clip {clip['rank']} | Score={clip['score']:.3f}"

def review_clip(i, label):
    if not clips: return "No clips"
    clips[i]["label"] = label
    return f"Saved feedback for clip {i+1}"

with gr.Blocks() as demo:
    gr.Markdown("# 🎬 Highlight Feedback Demo")
    video = gr.Video()
    transcript = gr.Textbox(label="Transcript")
    status_box = gr.Textbox(label="Status")

    with gr.Row():
        btn_prev = gr.Button("⬅ Prev")
        btn_next = gr.Button("Next ➡")
    with gr.Row():
        btn_good = gr.Button("👍 Good")
        btn_bad = gr.Button("👎 Bad")

    btn_prev.click(lambda i: max(0, i-1), inputs=idx, outputs=idx).then(load_clip, inputs=idx, outputs=[video, transcript, status_box])
    btn_next.click(lambda i: min(len(clips)-1, i+1), inputs=idx, outputs=idx).then(load_clip, inputs=idx, outputs=[video, transcript, status_box])

    btn_good.click(lambda i: review_clip(i, 1), inputs=idx, outputs=status_box)
    btn_bad.click(lambda i: review_clip(i, 0), inputs=idx, outputs=status_box)

    demo.load(load_clip, inputs=idx, outputs=[video, transcript, status_box])

if __name__ == "__main__":
    demo.launch()
