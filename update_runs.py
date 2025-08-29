import json, glob, os

RUNS_DIR = "runs"
OLD_PATH = "data/clips/"
NEW_PATH = "data/clips_compressed/"

for file in glob.glob(f"{RUNS_DIR}/*.json"):
    with open(file, "r") as f:
        data = json.load(f)

    for clip in data.get("clips", []):
        if "file" in clip and clip["file"].startswith(OLD_PATH):
            clip["file"] = clip["file"].replace(OLD_PATH, NEW_PATH)

    with open(file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {file}")
