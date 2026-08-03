from backend.scripts.split_book import read_book, remove_table_of_contents, extract_chapters, write_chapters

def test_read_book(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test function!")

    content = read_book(test_file)

    assert content == "This is a test function!"

def test_remove_table_of_contents():
    heading = "Chapter 1. Marseilles—The Arrival"

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
