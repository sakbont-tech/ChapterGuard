from backend.book_loader import load_metadata, validate_metadata
import json
import pytest

def test_load_metadata(tmp_path):
    test_metadata_data = {
        "id" : "GOT",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    test_metadata = tmp_path / "test_metadata.json"
    with open(test_metadata, "w", encoding="utf-8") as file:
        json.dump(test_metadata_data, file)

    metadata_dict = load_metadata(test_metadata)

    assert metadata_dict == test_metadata_data

def test_validate_metadata():
    test_metadata_data = {
        "id" : "GOT",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
    }

    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)