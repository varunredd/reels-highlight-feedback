import json, glob

RUNS_DIR = "runs"

# Base URL for your dataset repo
DATASET_URL = "https://huggingface.co/datasets/bharathreddy202/reels-clips/resolve/main/"

for file in glob.glob(f"{RUNS_DIR}/*.json"):
    with open(file, "r") as f:
        data = json.load(f)

    for clip in data.get("clips", []):
        if "file" in clip:
            # Always rewrite to dataset URL + filename
            filename = clip["file"].split("/")[-1]  # keep just clip_1.mp4 etc.
            clip["file"] = DATASET_URL + filename

    with open(file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {file}")
