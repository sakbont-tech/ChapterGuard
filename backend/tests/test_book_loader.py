from backend.book_loader import load_metadata, validate_metadata, load_chapter, load_chapters_up_to
import json
import pytest
from pathlib import Path

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

def test_load_chapter(tmp_path):
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    chapters_directory = tmp_path / "chapters"
    chapters_directory.mkdir()

    test_file = chapters_directory / f"chapter_{3:03}.txt"
    test_file.write_text("This is Chapter 3!")

    chapter = load_chapter(tmp_path, test_metadata_data, 3)

    assert chapter == "This is Chapter 3!"

def test_load_chapter_invalid_chapter(tmp_path):
    test_metadata_data = {
        "id" : "got",
        "title" : "A Game of Thrones",
        "author" : "George RR Martin",
        "language" : "English",
        "total_chapters" : 57,
        "chapters_directory" : "chapters",
        "source_url": "https://example.com/test-book.txt"    
    }

    with pytest.raises(ValueError):
        load_chapter(tmp_path, test_metadata_data, 99)

def test_load_chapters_up_to(tmp_path):
    metadata = {
        "id": "got",
        "title": "A Game of Thrones",
        "author": "George RR Martin",
        "language": "English",
        "total_chapters": 57,
        "chapters_directory": "chapters",
        "source_url": "https://example.com/test-book.txt",
    }

    chapters_directory = tmp_path / "chapters"
    chapters_directory.mkdir()

    for chapter_number in range(1, 4):
        chapter_file = chapters_directory / f"chapter_{chapter_number:03}.txt"
        chapter_file.write_text(
            f"This is Chapter {chapter_number}!",
            encoding="utf-8",
        )

    chapters = load_chapters_up_to(tmp_path, metadata, 3)

    assert chapters == (
        "This is Chapter 1!\n\n"
        "This is Chapter 2!\n\n"
        "This is Chapter 3!"
    )

def test_load_chapters_up_to_with_count_of_monte_cristo():
    book_directory = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "books"
        / "count_of_monte_cristo"
    )

    metadata = load_metadata(book_directory / "metadata.json")
    validate_metadata(metadata)

    chapters = load_chapters_up_to(
        book_directory,
        metadata,
        3,
    )

    assert "Chapter 1. Marseilles—The Arrival" in chapters
    assert "Chapter 2. Father and Son" in chapters
    assert "Chapter 3. The Catalans" in chapters
    assert "Chapter 4. Conspiracy" not in chapters