import json
from pathlib import Path

def load_metadata(metadata_path: Path):
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    return metadata 