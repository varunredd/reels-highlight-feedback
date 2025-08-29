<<<<<<< HEAD
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

📂 Project Structure

Reels/
├── data/ # Videos, audio, transcripts, clips
├── models/ # Trained highlight detector
├── notebooks/ # Review + feedback collection notebooks
├── src/ml/ # ML scripts (train, inference, dataset builder)
├── run_full_cycle.sh # End-to-end automation script
└── gradio_feedback_demo.py # UI entrypoint


🔮 Roadmap

 Collect at least 500+ feedback samples

 Train the improved transformer model on user feedback

 Add multi-user support (track who gave which feedback)

 Deploy refined model for real-time highlight detection

🙌 Acknowledgements

🤗 Hugging Face
 for hosting the demo

Gradio
 for simple web UIs

OpenAI Whisper
 for subtitle generation
=======
---
title: friends
app_file: app.py
sdk: gradio
sdk_version: 5.44.1
---
>>>>>>> 3cb2994 (Initial project commit with pipeline + feedback demo)
