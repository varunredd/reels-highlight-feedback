"""
Phase 3 - Clip Extractor with optional subtitle overlay
"""

import ffmpeg

def cut_clip(input_video: str, start: str, end: str, output_file: str):
    """Cut a video segment using ffmpeg (no subtitles)."""
    stream = (
        ffmpeg
        .input(input_video, ss=start, to=end)
        .output(output_file, codec="copy")
        .overwrite_output()
    )
    ffmpeg.run(stream)

def burn_subtitles(input_video: str, subtitle_file: str, output_file: str):
    """Burn subtitles into video permanently."""
    stream = (
        ffmpeg
        .input(input_video)
        .output(output_file, vf=f"subtitles={subtitle_file}")
        .overwrite_output()
    )
    ffmpeg.run(stream)

def cut_with_subtitles(input_video: str, start: str, end: str, subtitle_file: str, output_file: str):
    """Cut video segment and burn subtitles in one step."""
    stream = (
        ffmpeg
        .input(input_video, ss=start, to=end)
        .output(output_file, vf=f"subtitles={subtitle_file}")
        .overwrite_output()
    )
    ffmpeg.run(stream)

if __name__ == "__main__":
    # Example usage:
    # Just cut
    cut_clip("data/videos/sample.mp4", "00:00:05", "00:00:15", "data/clips/clip1.mp4")
    
    # Burn subtitles separately
    burn_subtitles("data/clips/clip1.mp4", "data/transcripts/sample.srt", "data/clips/clip1_subs.mp4")
    
    # Or do both in one step
    cut_with_subtitles("data/videos/sample.mp4", "00:00:05", "00:00:15",
                       "data/transcripts/sample.srt", "data/clips/clip2_with_subs.mp4")
