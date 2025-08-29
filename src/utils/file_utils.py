import shutil
from pathlib import Path

def ensure_dir(path: str):
    """Make sure a directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def clear_dir(path: str):
    """Delete all files inside a directory but keep the folder."""
    p = Path(path)
    if p.exists():
        for item in p.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        p.mkdir(parents=True, exist_ok=True)
