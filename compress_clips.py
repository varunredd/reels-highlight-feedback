import subprocess
from pathlib import Path

INPUT_DIR = Path("data/clips")
OUTPUT_DIR = Path("data/clips_compressed")

# Create output folder
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def compress_video(in_file: Path, out_file: Path):
    """
    Compress video using ffmpeg (240p, low bitrate, keep audio).
    """
    cmd = [
        "ffmpeg",
        "-y",                      # overwrite without asking
        "-i", str(in_file),        # input file
        "-vf", "scale=426:240",    # resize to 240p
        "-b:v", "500k",            # set video bitrate
        "-c:a", "aac",             # encode audio with AAC
        "-b:a", "64k",             # compress audio to 64 kbps
        str(out_file)
    ]
    print(f"🎬 Compressing {in_file} -> {out_file}")
    subprocess.run(cmd, check=True)

def main():
    mp4_files = list(INPUT_DIR.glob("*.mp4"))
    if not mp4_files:
        print("⚠️ No .mp4 files found in", INPUT_DIR)
        return

    for f in mp4_files:
        out_f = OUTPUT_DIR / f.name
        compress_video(f, out_f)

    print(f"\n✅ Compression finished. Compressed files are in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
