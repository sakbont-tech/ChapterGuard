import json
from pathlib import Path

def load_metadata(metadata_path: Path):
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    return metadata

def validate_metadata(metadata):
    required_fields = {
        "id",
        "title",
        "author",
        "language",
        "total_chapters",
        "chapters_directory",
        "source_url",
    }

    missing_fields = required_fields - metadata.keys()

    if missing_fields:
        raise ValueError(
            f"Missing required metadata fields: {sorted(missing_fields)}"
        )