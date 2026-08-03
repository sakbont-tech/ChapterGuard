from backend.scripts.split_book import read_book, remove_table_of_contents, extract_chapters, write_chapters

def test_read_book(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test function!")

    content = read_book(test_file)

    assert content == "This is a test function!"

def test_remove_table_of_contents():
    content = (
        "Chapter 1. Marseilles—The Arrival\n"
        "Chapter 2. Father and Son\n"
        "Chapter 3. The Catalans\n"
        "Chapter 4. Conspiracy\n"
        "\n"
        "Chapter 1. Marseilles—The Arrival\n"
        "On the 24th of February, 1815, the story begins."
    )

    result = remove_table_of_contents(content)

    assert result == (
        "Chapter 1. Marseilles—The Arrival\n"
        "On the 24th of February, 1815, the story begins."
    )

def test_extract_chapters():
    test_content = ("Chapter 1. Marseilles—The Arrival\n"
    "On the 24th of February, 1815, the story begins.\n"
    "Chapter 2. Father and Son\n"
    "The son and the father blah blah\n"
    "Chapter 3. The Catalans\n"
    "HELLOOOOOO"
    "FOOTNOTES: this is a footnote")

    test_list = extract_chapters(test_content, 3)

    assert len(test_list) == 3
    assert test_list[0] == ("Chapter 1. Marseilles—The Arrival\n"
    "On the 24th of February, 1815, the story begins.\n")

def test_write_chapters(tmp_path):
    # Arrange
    chapter_list = [
        "Chapter 1. First\nThis is chapter one.",
        "Chapter 2. Second\nThis is chapter two.",
    ]
    chapter_folder = tmp_path / "chapters"

    # Act
    write_chapters(chapter_list, chapter_folder)

    # Assert
    chapter_one = chapter_folder / "chapter_001.txt"
    chapter_two = chapter_folder / "chapter_002.txt"

    assert chapter_one.exists()
    assert chapter_two.exists()

    assert chapter_one.read_text(encoding="utf-8") == chapter_list[0]
    assert chapter_two.read_text(encoding="utf-8") == chapter_list[1]

    assert len(list(chapter_folder.iterdir())) == 2