from backend.scripts.split_book import read_book, remove_table_of_contents, extract_chapters, write_chapters


def test_read_book(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test function!")

    content = read_book(test_file)

    assert content == "This is a test function!"