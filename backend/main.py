from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import AskRequest, AskResponse
from backend.database import Request, get_async_session, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from backend.book_loader import get_book_context, load_book

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["Content-Type"]
)

SUPPORTED_BOOK_IDS = [
    "count_of_monte_cristo",
]

book_requests = {
    1: {
        "title": "Dune",
        "chapter": 15,
        "question": "Who is Paul?"
    },
    2: {
        "title": "Harry Potter and the Philosopher's Stone",
        "chapter": 6,
        "question": "Who is Hagrid?"
    }
}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/books")
def get_books():
    books = []

    for book_id in SUPPORTED_BOOK_IDS:
        _, metadata = load_book(book_id)

        books.append({
            "book_id": metadata["id"],
            "title": metadata["title"],
            "total_chapters": metadata["total_chapters"],
        })

    return books

@app.post("/ask")
def ask_question(request: AskRequest) -> AskResponse:
    new_request = {
        "book_id": request.book_id,
        "current_chapter": request.current_chapter,
        "question": request.question
    }
    context = get_book_context(new_request["book_id"], new_request["current_chapter"])
    new_id = max(book_requests.keys()) + 1
    book_requests[new_id] = new_request
    return AskResponse(
        book_id=request.book_id,
        current_chapter=request.current_chapter,
        question=request.question,
        answer="This is a spoiler free response!"
    )

