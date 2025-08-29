🎬 Reels Highlight Feedback

An interactive web app for reviewing and labeling video highlight clips.
Your feedback will be used to train and improve our highlight detection AI model (a transformer-based text regressor).

🚀 How it works

Upload a video 🎥 → The system automatically:

Extracts audio

Generates subtitles (Whisper)

Detects highlight-worthy moments (AI model)

Cuts them into short clips

Review the clips 🖥️ → For each clip:

Watch the video preview

Read the transcript

Mark 👍 Good Highlight or 👎 Not a Highlight

Feedback is stored → All ratings are consolidated into a dataset (feedback.jsonl)
This dataset is later used to fine-tune the highlight detection model.

🛠️ Tech Stack

Backend pipeline: Python, FFmpeg, OpenAI Whisper

Model: DistilBERT regressor (fine-tuned for highlight scoring)

Web UI: Gradio
on Hugging Face Spaces

Dataset storage: JSONL feedback logs

📊 Why this matters

Highlight detection is subjective — different people may find different parts of a video exciting or important.
By collecting real user feedback, we make the AI model more accurate and personalized over time.

👩‍💻 Contribute

Visit the demo: Click here to try it on Hugging Face Spaces

Review a few clips and submit your feedback 👍👎

That’s it! You’ve contributed to training a better AI 🎉
