"""
Pipeline runner: video -> audio -> transcript -> highlights -> clips
"""

import json, datetime, os, shutil
from pathlib import Path
from src.extract_subtitles import extract_subtitles
from src.highlight_detector import extract_highlights
from src.clip_extractor import cut_clip, cut_with_subtitles
from src.utils.file_utils import ensure_dir
from src.utils.subtitle_utils import trim_srt_to_range
from src.utils.audio_utils import extract_audio_from_video, align_to_silence


# Toggle features
USE_SUBTITLES = False        # Burn subtitles into final clips
ALIGN_TO_SILENCE = True      # Snap clip boundaries to nearest silence
TOP_N_HIGHLIGHTS = 5         # Number of clips to generate


def auto_clean():
    """Remove old files from data/audio, data/clips, data/transcripts."""
    for folder in ["data/audio", "data/clips", "data/transcripts"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    print("🧹 Cleaned previous run files.")


def srt_time_to_seconds(srt_time: str) -> float:
    """Convert 'HH:MM:SS,ms' to float seconds."""
    h, m, s_ms = srt_time.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def seconds_to_ffmpeg_time(seconds: float) -> str:
    """Convert float seconds to 'HH:MM:SS.mmm' for ffmpeg."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}"


def run_pipeline(video_file: str):
    auto_clean()  # 🧹 Clear old data before each run

    audio_file = "data/audio/temp_audio.mp3"
    transcript_file = "data/transcripts/output.srt"
    ensure_dir("data/audio")
    ensure_dir("data/transcripts")
    ensure_dir("data/clips")

    # Step 1: Extract audio
    print("🎙️ Extracting audio...")
    extract_audio_from_video(video_file, audio_file)

    # Step 2: Extract subtitles
    print("▶️ Extracting subtitles...")
    extract_subtitles(audio_file, transcript_file)

    # Step 3: Detect highlight segments (ML or keywords)
    print("⭐ Detecting highlights...")
    highlights = extract_highlights(transcript_file, top_n=TOP_N_HIGHLIGHTS)

    if not highlights:
        print("⚠️ No highlights detected. Try adjusting keywords or re-training model.")
        return []

    # Step 4: Cut clips
    print("✂️ Cutting clips...")
    clips_info = []
    for i, (score, _, times, text) in enumerate(highlights, start=1):
        start_srt, end_srt = times.split(" --> ")

        # Convert SRT → seconds
        start_sec = srt_time_to_seconds(start_srt)
        end_sec = srt_time_to_seconds(end_srt)

        # Optional: snap to silence
        if ALIGN_TO_SILENCE:
            adj_start, adj_end = align_to_silence(audio_file, start_sec, end_sec)
        else:
            adj_start, adj_end = start_sec, end_sec

        # Convert to ffmpeg format
        start_ff = seconds_to_ffmpeg_time(adj_start)
        end_ff = seconds_to_ffmpeg_time(adj_end)

        # Debug log
        snippet = text[:60] + ("..." if len(text) > 60 else "")
        print(f"🎬 Clip {i}: {start_ff} → {end_ff} | Score={score:.3f} | {snippet}")

        # Handle subtitles
        if USE_SUBTITLES:
            mini_srt = f"data/transcripts/clip_{i}.srt"
            trim_srt_to_range(transcript_file, start_srt, end_srt, mini_srt)
            out = f"data/clips/clip_{i}_subs.mp4"
            cut_with_subtitles(video_file, start_ff, end_ff, mini_srt, out)
        else:
            out = f"data/clips/clip_{i}.mp4"
            cut_clip(video_file, start_ff, end_ff, out)

        print(f"✅ Created {out}")

        # Save clip info for logging
        clips_info.append({
            "rank": i,
            "score": score,
            "times": times,
            "text": text,
            "file": out
        })

    return clips_info


def log_run(video_file, highlights, model_used="transformer"):
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    Path("runs").mkdir(exist_ok=True)
    log_file = f"runs/{ts}.json"
    log_data = {
        "timestamp": ts,
        "video": video_file,
        "model_used": model_used,
        "num_highlights": len(highlights),
        "clips": highlights
    }
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"📝 Logged run to {log_file}")


if __name__ == "__main__":
    video_file = "data/videos/output.mp4"
    highlights = run_pipeline(video_file)
    if highlights:
        log_run(video_file, highlights, model_used="transformer")
