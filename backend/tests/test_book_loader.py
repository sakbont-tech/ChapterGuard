from backend.book_loader import load_metadata
import json

def test_load_metadata(tmp_path):
    test_metadata_data = {
        "id" : "GOT",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total chapters" : 57,
        "chapters directory" : "chapters",
        "source_url": "https://www.gutenberg.org/cache/epub/1184/pg1184.txt"
    }

    test_metadata = tmp_path / "test_metadata.json"
    with open(test_metadata, "w", encoding="utf-8") as file:
        json.dump(test_metadata_data, file)

    metadata_dict = load_metadata(test_metadata)

    assert metadata_dict == test_metadata_data