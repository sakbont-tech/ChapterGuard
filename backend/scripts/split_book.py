from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
book_path = (
    backend_path
    / "data"
    / "books"
    / "count_of_monte_cristo"
)

raw_path = book_path / "raw.txt"
chapter_folder_path = book_path / "chapters"
total_chapters = 117

def read_book(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content

def remove_table_of_contents(content):
    heading = "Chapter 1. Marseilles—The Arrival"

    first_occurrence = content.find(heading)

    if first_occurrence == -1:
        raise ValueError("The first Chapter 1 heading was not found.")
    
    second_occurrence = content.find(heading, first_occurrence + len(heading))

    if second_occurrence == -1:
        raise ValueError("The second Chapter 1 heading was not found.")
    
    book_onward = content[second_occurrence:]
    return book_onward

def extract_chapters(book_onward, total_chapters):
    chapter_list = []

    for chapter_number in range(1, total_chapters + 1):
        chapter_heading = f"Chapter {chapter_number}."
        next_chapter_heading = f"Chapter {chapter_number + 1}."
        current_chapter_start = book_onward.find(chapter_heading)
        if(current_chapter_start == -1):
            raise ValueError(f"Chapter heading {chapter_number} was not found")
        if(chapter_number == total_chapters):
            footer = book_onward.find("FOOTNOTES:", current_chapter_start)
            if footer == -1:
                raise ValueError("FOOTNOTES was not found.")
            chapter = book_onward[current_chapter_start:footer]
        else:
            current_chapter_end = book_onward.find(next_chapter_heading, current_chapter_start + len(chapter_heading))
            if current_chapter_end == -1:
                raise ValueError(f"Chapter heading {chapter_number + 1} was not found.")
            chapter = book_onward[current_chapter_start:current_chapter_end]
        chapter_list.append(chapter)
    return chapter_list

def write_chapters(chapter_list, chapter_folder_path):
    chapter_folder_path.mkdir(parents=True, exist_ok=True)
    for chapter_number, chapter in enumerate(chapter_list, start=1):
        chapter_path = chapter_folder_path / f"chapter_{chapter_number:03}.txt"
        chapter_path.write_text(chapter, encoding="utf-8")
        print(f"Created {chapter_path.name}")

def main():
    content = read_book(raw_path)
    book_onward = remove_table_of_contents(content)
    chapter_list = extract_chapters(book_onward, total_chapters)
    write_chapters(chapter_list, chapter_folder_path)

if __name__ == "__main__":
    main()