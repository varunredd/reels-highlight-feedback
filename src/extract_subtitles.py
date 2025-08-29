import whisper
from pathlib import Path

def extract_subtitles(audio_path: str, output_srt: str, model_size="base"):
    """Transcribe audio and save subtitles in SRT format."""
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)

    def format_time(seconds: float) -> str:
        hrs, secs = divmod(int(seconds), 3600)
        mins, secs = divmod(secs, 60)
        millis = int((seconds % 1) * 1000)
        return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

    with open(output_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], start=1):
            start = format_time(seg["start"])
            end = format_time(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

if __name__ == "__main__":
    audio_file = "data/audio/sample.m4a"
    output_srt = "data/transcripts/sample.srt"
    Path("data/transcripts").mkdir(parents=True, exist_ok=True)
    extract_subtitles(audio_file, output_srt)