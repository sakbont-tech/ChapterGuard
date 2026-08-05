from backend.book_loader import load_metadata, validate_metadata
import json
import pytest

def test_load_metadata(tmp_path):
    test_metadata_data = {
        "id" : "got",
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

    correct_test_metadata = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"   
    }

    assert validate_metadata(correct_test_metadata) is None

def test_missing_metadata():
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
    }
        
    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)

def test_wrong_metadata_field():
    test_metadata_data = {
        "id" : "got",
        "title" : 123,
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(TypeError):
        validate_metadata(test_metadata_data)

def test_empty_metadata():
    test_metadata_data = {
        "id" : "got",
        "title" : "     ",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)

def test_total_chapters_not_integer():
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : "string",
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(TypeError):
        validate_metadata(test_metadata_data)

def test_total_chapters_equal_zero():
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 0,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)

def test_invalid_id():
    test_metadata_data = {
        "id" : "GOT",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 123,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)

def test_invalid_chapters_directory():
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 123,
        "chapters_directory" : "C://Users/saketh/chapters/adbasdha/aierhwqoeq",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(ValueError):
        validate_metadata(test_metadata_data)
