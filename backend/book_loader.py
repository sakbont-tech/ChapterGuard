import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

def load_metadata(metadata_path: Path):
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, dict):
        raise TypeError("Metadata must be a JSON object")

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
    
    text_fields = {
        "id",
        "title",
        "author",
        "language",
        "chapters_directory",
        "source_url",
    }

    for field in text_fields:
        if not isinstance(metadata[field], str):
            raise TypeError(f"{field} must be a string")

    for field in text_fields:
        if not metadata[field].strip():
            raise ValueError(f"{field} must not be empty")

    if type(metadata["total_chapters"]) is not int:
        raise TypeError("total_chapters must be an integer")

    if metadata["total_chapters"] <= 0:
        raise ValueError("Total chapters must be greater than 0")

    if not re.fullmatch(r"[a-z0-9_]+", metadata["id"]):
        raise ValueError(
            "id may contain only lowercase letters, numbers, and underscores"
        )

    chapters_directory = metadata["chapters_directory"]
    posix_path = PurePosixPath(chapters_directory)
    windows_path = PureWindowsPath(chapters_directory)

    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in posix_path.parts
        or ".." in windows_path.parts
    ):
        raise ValueError(
            "chapters_directory must be a safe relative path"
        )

def load_chapter(book_directory, metadata, chapter_number):
    if not (1 <= chapter_number <= metadata["total_chapters"]):
        raise ValueError(f"{chapter_number} is out of bounds")

    chapter_path = book_directory / metadata["chapters_directory"] / f"{chapter_number:03}.txt"

    with open(chapter_path, "r", encoding="utf-8") as file:
        chapter = file.read()
    return chapter

def load_chapters_up_to(book_directory, metadata, chapter_until):
    if not 1 <= chapter_until <= metadata["total_chapters"]:
        raise ValueError(f"{chapter_until} is out of bounds")

    chapters = []

    for chapter_number in range(1, chapter_until + 1):
        chapter = load_chapter(book_directory, metadata, chapter_number)
        chapters.append(chapter)

    return "\n\n".join(chapters)