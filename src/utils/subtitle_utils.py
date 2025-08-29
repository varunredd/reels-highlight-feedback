"""
Subtitle utilities: trim SRT to clip timeframe
"""

from pathlib import Path

def parse_srt_time(srt_time: str) -> float:
    """Convert SRT time 'HH:MM:SS,ms' to seconds."""
    h, m, s_ms = srt_time.split(":")
    s, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def format_srt_time(seconds: float) -> str:
    """Convert seconds back to SRT format 'HH:MM:SS,ms'."""
    hrs, secs = divmod(int(seconds), 3600)
    mins, secs = divmod(secs, 60)
    millis = int((seconds % 1) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def trim_srt_to_range(input_srt: str, start: str, end: str, output_srt: str):
    """Create a mini SRT file only containing lines within [start, end]."""
    clip_start = parse_srt_time(start)
    clip_end = parse_srt_time(end)

    with open(input_srt, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")

    new_blocks = []
    counter = 1

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            times = lines[1]
            s, e = times.split(" --> ")
            seg_start = parse_srt_time(s)
            seg_end = parse_srt_time(e)

            # Keep only captions inside clip window
            if seg_start >= clip_start and seg_end <= clip_end:
                # Shift relative to clip start
                new_start = format_srt_time(seg_start - clip_start)
                new_end = format_srt_time(seg_end - clip_start)
                text = " ".join(lines[2:])
                new_block = f"{counter}\n{new_start} --> {new_end}\n{text}"
                new_blocks.append(new_block)
                counter += 1

    Path(output_srt).parent.mkdir(parents=True, exist_ok=True)
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(new_blocks))
