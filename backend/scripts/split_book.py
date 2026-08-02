from pathlib import Path

file_path = Path(r"C:\Users\SAKPAV\git\ChapterGuard\backend\data\books\count_of_monte_cristo\raw.txt")
chapter_folder_path = Path(r"C:\Users\SAKPAV\git\ChapterGuard\backend\data\books\count_of_monte_cristo\chapters")
chapter_folder_path.mkdir(parents=True, exist_ok=True)

with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

first_occurrence = content.find("Chapter 1. Marseilles—The Arrival")
second_occurrence = content.find("Chapter 1. Marseilles—The Arrival", first_occurrence + 1)

book_onward = content[second_occurrence:]
####################################################################################################################################
total_chapters = 117


for i in range(1, total_chapters + 1):
    chapter_path = chapter_folder_path / f"chapter_{i:03}.txt"
    current_chapter_start = book_onward.find(f"Chapter {i}.")
    current_chapter_end = book_onward.find(f"Chapter {i + 1}.")
    if current_chapter_end == -1:
        footer = book_onward.find("FOOTNOTES:")
        chapter = book_onward[current_chapter_start:footer]
    else:
        chapter = book_onward[current_chapter_start:current_chapter_end]
    chapter_path.write_text(chapter, encoding="utf-8")
    print(f"Created {chapter_path.name}")