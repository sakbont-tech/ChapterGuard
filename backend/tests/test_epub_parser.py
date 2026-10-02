from io import BytesIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest

from backend import epub_parser
from backend.epub_parser import (
    EpubLimitError,
    InvalidEpubError,
    NoUsableTextError,
    UnsupportedDrmError,
    parse_epub,
)


FILE_HASH = "a" * 64
CONTAINER_XML = """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OPS/package.opf"
              media-type="application/oebps-package+xml" />
  </rootfiles>
</container>
"""


def xhtml(body, *, title="", body_attributes=""):
    return f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops">
  <head><title>{title}</title></head>
  <body {body_attributes}>{body}</body>
</html>
"""


def make_epub(
    *,
    manifest_items,
    spine_ids,
    files,
    metadata="""
      <dc:title>Test Book</dc:title>
      <dc:creator>Test Author</dc:creator>
      <dc:language>en</dc:language>
    """,
    guide="",
    spine_attributes="",
):
    manifest = "\n".join(
        f'<item id="{item_id}" href="{href}" media-type="{media_type}"'
        f'{f" properties={properties!r}" if properties else ""} />'
        for item_id, href, media_type, properties in manifest_items
    )
    spine = "\n".join(
        f'<itemref idref="{item_id}"{f" linear={linear!r}" if linear else ""} />'
        for item_id, linear in spine_ids
    )
    package = f"""<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">
  <metadata>{metadata}</metadata>
  <manifest>{manifest}</manifest>
  <spine {spine_attributes}>{spine}</spine>
  {guide}
</package>
"""

    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        archive.writestr(
            "META-INF/container.xml", CONTAINER_XML, compress_type=ZIP_DEFLATED
        )
        archive.writestr("OPS/package.opf", package, compress_type=ZIP_DEFLATED)
        for name, content in files.items():
            archive.writestr(name, content, compress_type=ZIP_DEFLATED)
    output.seek(0)
    return output


def test_parse_epub_returns_metadata_and_spine_order():
    nav = xhtml(
        """
        <nav epub:type="toc"><ol>
          <li><a href="chapter-2.xhtml#start">The Second Chapter</a></li>
          <li><a href="chapter-1.xhtml">The First Chapter</a></li>
        </ol></nav>
        """
    )
    book = make_epub(
        manifest_items=[
            ("nav", "nav.xhtml", "application/xhtml+xml", "nav"),
            ("one", "chapter-1.xhtml", "application/xhtml+xml", ""),
            ("two", "chapter-2.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("nav", "no"), ("one", ""), ("two", "")],
        files={
            "OPS/nav.xhtml": nav,
            "OPS/chapter-1.xhtml": xhtml(
                "<h1>Ignored heading title</h1><p>Hello <em>brave</em> world.</p>"
            ),
            "OPS/chapter-2.xhtml": xhtml("<p>Second section.</p>"),
        },
    )

    result = parse_epub(
        book, original_filename="upload.epub", file_hash=FILE_HASH.upper()
    )

    assert result.title == "Test Book"
    assert result.author == "Test Author"
    assert result.language == "en"
    assert result.file_hash == FILE_HASH
    assert [chapter.chapter_number for chapter in result.chapters] == [1, 2]
    assert [chapter.title for chapter in result.chapters] == [
        "The First Chapter",
        "The Second Chapter",
    ]
    assert result.chapters[0].content == (
        "Ignored heading title\n\nHello brave world."
    )


def test_title_fallbacks_empty_documents_and_missing_metadata():
    book = make_epub(
        metadata="",
        manifest_items=[
            ("empty", "empty.xhtml", "application/xhtml+xml", ""),
            ("heading", "heading.xhtml", "application/xhtml+xml", ""),
            ("document-title", "document-title.xhtml", "application/xhtml+xml", ""),
            ("untitled", "untitled.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[
            ("empty", ""),
            ("heading", ""),
            ("document-title", ""),
            ("untitled", ""),
        ],
        files={
            "OPS/empty.xhtml": xhtml("   "),
            "OPS/heading.xhtml": xhtml("<h2>From heading</h2><p>Text.</p>"),
            "OPS/document-title.xhtml": xhtml(
                "<p>More text.</p>", title="From document title"
            ),
            "OPS/untitled.xhtml": xhtml("<p>Final text.</p>"),
        },
    )

    result = parse_epub(
        book,
        original_filename=r"C:\fake-client-path\Fallback Name.epub",
        file_hash=FILE_HASH,
    )

    assert result.title == "Fallback Name"
    assert result.author is None
    assert result.language == "und"
    assert [chapter.chapter_number for chapter in result.chapters] == [1, 2, 3]
    assert [chapter.title for chapter in result.chapters] == [
        "From heading",
        "From document title",
        None,
    ]


def test_identifiable_front_matter_is_excluded():
    nav = xhtml(
        """
        <nav epub:type="landmarks"><ol>
          <li><a epub:type="dedication" href="dedication.xhtml">Dedication</a></li>
        </ol></nav>
        """
    )
    guide = """
      <guide>
        <reference type="cover" href="cover.xhtml" />
      </guide>
    """
    book = make_epub(
        manifest_items=[
            ("nav", "nav.xhtml", "application/xhtml+xml", "nav"),
            ("cover", "cover.xhtml", "application/xhtml+xml", ""),
            ("dedication", "dedication.xhtml", "application/xhtml+xml", ""),
            ("copyright", "copyright.xhtml", "application/xhtml+xml", ""),
            ("chapter", "chapter.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[
            ("cover", ""),
            ("dedication", ""),
            ("copyright", ""),
            ("chapter", ""),
        ],
        guide=guide,
        files={
            "OPS/nav.xhtml": nav,
            "OPS/cover.xhtml": xhtml("<p>Cover</p>"),
            "OPS/dedication.xhtml": xhtml("<p>For someone</p>"),
            "OPS/copyright.xhtml": xhtml(
                "<p>Copyright notice</p>", body_attributes='epub:type="copyright-page"'
            ),
            "OPS/chapter.xhtml": xhtml("<h1>Chapter One</h1><p>Story.</p>"),
        },
    )

    result = parse_epub(book, original_filename="book.epub", file_hash=FILE_HASH)

    assert len(result.chapters) == 1
    assert result.chapters[0].title == "Chapter One"


def test_each_usable_spine_document_becomes_one_section():
    book = make_epub(
        manifest_items=[
            ("part-a", "part-a.xhtml", "application/xhtml+xml", ""),
            ("part-b", "part-b.xhtml", "application/xhtml+xml", ""),
            ("two-chapters", "two-chapters.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("part-a", ""), ("part-b", ""), ("two-chapters", "")],
        files={
            "OPS/part-a.xhtml": xhtml("<h1>Part A</h1><p>Text A.</p>"),
            "OPS/part-b.xhtml": xhtml("<h1>Part B</h1><p>Text B.</p>"),
            "OPS/two-chapters.xhtml": xhtml(
                "<h1>Chapter Two</h1><p>Two.</p><h1>Chapter Three</h1><p>Three.</p>"
            ),
        },
    )

    result = parse_epub(book, original_filename="book.epub", file_hash=FILE_HASH)

    assert len(result.chapters) == 3
    assert result.chapters[2].title == "Chapter Two"
    assert "Chapter Three" in result.chapters[2].content


def test_epub2_ncx_titles_are_supported():
    ncx = """<?xml version="1.0"?>
    <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
                          "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/">
      <navMap><navPoint>
        <navLabel><text>NCX Chapter</text></navLabel>
        <content src="chapter.xhtml#chapter" />
      </navPoint></navMap>
    </ncx>
    """
    book = make_epub(
        manifest_items=[
            ("ncx", "toc.ncx", "application/x-dtbncx+xml", ""),
            ("chapter", "chapter.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("chapter", "")],
        spine_attributes='toc="ncx"',
        files={
            "OPS/toc.ncx": ncx,
            "OPS/chapter.xhtml": xhtml("<p>Story.</p>"),
        },
    )

    result = parse_epub(book, original_filename="book.epub", file_hash=FILE_HASH)

    assert result.chapters[0].title == "NCX Chapter"


def test_invalid_zip_is_rejected():
    with pytest.raises(InvalidEpubError):
        parse_epub(
            BytesIO(b"not a zip"),
            original_filename="broken.epub",
            file_hash=FILE_HASH,
        )


def test_archive_without_epub_mimetype_is_rejected():
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("something.txt", "not an epub")
    output.seek(0)

    with pytest.raises(InvalidEpubError, match="mimetype"):
        parse_epub(output, original_filename="broken.epub", file_hash=FILE_HASH)


def test_unsafe_archive_path_is_rejected():
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        archive.writestr("OPS/../outside.xhtml", "unsafe")
    output.seek(0)

    with pytest.raises(InvalidEpubError, match="unsafe archive path"):
        parse_epub(output, original_filename="unsafe.epub", file_hash=FILE_HASH)


def test_epub_with_no_usable_text_is_rejected():
    book = make_epub(
        manifest_items=[
            ("empty", "empty.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("empty", "")],
        files={"OPS/empty.xhtml": xhtml("  ")},
    )

    with pytest.raises(NoUsableTextError):
        parse_epub(book, original_filename="empty.epub", file_hash=FILE_HASH)


def test_encrypted_spine_document_is_rejected():
    encryption_xml = """<?xml version="1.0"?>
    <encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
                xmlns:enc="http://www.w3.org/2001/04/xmlenc#">
      <enc:EncryptedData>
        <enc:CipherData><enc:CipherReference URI="OPS/chapter.xhtml" /></enc:CipherData>
      </enc:EncryptedData>
    </encryption>
    """
    book = make_epub(
        manifest_items=[
            ("chapter", "chapter.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("chapter", "")],
        files={
            "OPS/chapter.xhtml": b"encrypted bytes",
            "META-INF/encryption.xml": encryption_xml,
        },
    )

    with pytest.raises(UnsupportedDrmError):
        parse_epub(book, original_filename="protected.epub", file_hash=FILE_HASH)


def test_archive_safety_limit_is_enforced(monkeypatch):
    book = make_epub(
        manifest_items=[
            ("chapter", "chapter.xhtml", "application/xhtml+xml", ""),
        ],
        spine_ids=[("chapter", "")],
        files={"OPS/chapter.xhtml": xhtml("<p>Story.</p>")},
    )
    monkeypatch.setattr(epub_parser, "MAX_ARCHIVE_ENTRIES", 2)

    with pytest.raises(EpubLimitError, match="too many"):
        parse_epub(book, original_filename="large.epub", file_hash=FILE_HASH)


def test_invalid_file_hash_is_rejected_before_parsing():
    with pytest.raises(ValueError, match="SHA-256"):
        parse_epub(
            BytesIO(b"anything"),
            original_filename="book.epub",
            file_hash="not-a-hash",
        )
