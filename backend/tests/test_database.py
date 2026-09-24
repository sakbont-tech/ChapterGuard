import pytest
from sqlalchemy import delete, event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from backend.database import Base, Book, Chapter, enable_sqlite_foreign_keys


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def session(anyio_backend):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    event.listen(engine.sync_engine, "connect", enable_sqlite_foreign_keys)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as database_session:
        yield database_session

    await engine.dispose()


def make_book(book_id, file_hash):
    return Book(
        id=book_id,
        title=f"Book {book_id}",
        author="Test Author",
        language="English",
        file_hash=file_hash,
    )


@pytest.mark.anyio
async def test_create_book_with_multiple_chapters(session):
    book = make_book("book-one", "a" * 64)
    book.chapters = [
        Chapter(chapter_number=1, title="One", content="Chapter one"),
        Chapter(chapter_number=2, title="Two", content="Chapter two"),
    ]

    session.add(book)
    await session.commit()
    session.expunge_all()

    result = await session.execute(
        select(Book).options(selectinload(Book.chapters)).where(Book.id == "book-one")
    )
    saved_book = result.scalar_one()

    saved_chapters = saved_book.chapters
    chapter_one, chapter_two = saved_chapters

    assert saved_book.total_chapters == 2

    assert chapter_one.chapter_number == 1
    assert chapter_two.chapter_number == 2

    assert chapter_one.book is saved_book
    assert chapter_two.book is saved_book


@pytest.mark.anyio
async def test_chapter_number_is_unique_within_a_book(session):
    book = make_book("book-one", "a" * 64)
    book.chapters = [
        Chapter(chapter_number=1, title="One", content="First copy"),
        Chapter(chapter_number=1, title="One again", content="Second copy"),
    ]
    session.add(book)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.anyio
async def test_same_chapter_number_is_allowed_for_different_books(session):
    first_book = make_book("book-one", "a" * 64)
    second_book = make_book("book-two", "b" * 64)
    first_book.chapters.append(
        Chapter(chapter_number=1, title="One", content="First book")
    )
    second_book.chapters.append(
        Chapter(chapter_number=1, title="One", content="Second book")
    )
    session.add_all([first_book, second_book])

    await session.commit()

    chapter_count = await session.scalar(select(func.count(Chapter.id)))
    assert chapter_count == 2


@pytest.mark.anyio
async def test_file_hash_is_unique(session):
    session.add_all(
        [
            make_book("book-one", "a" * 64),
            make_book("book-two", "a" * 64),
        ]
    )

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.anyio
async def test_deleting_book_deletes_its_chapters(session):
    book = make_book("book-one", "a" * 64)
    book.chapters = [
        Chapter(chapter_number=1, title="One", content="Chapter one"),
        Chapter(chapter_number=2, title="Two", content="Chapter two"),
    ]
    session.add(book)
    await session.commit()

    await session.execute(delete(Book).where(Book.id == "book-one"))
    await session.commit()

    chapter_count = await session.scalar(select(func.count(Chapter.id)))
    assert chapter_count == 0
