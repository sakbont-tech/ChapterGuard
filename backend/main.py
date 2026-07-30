from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import AskRequest, AskResponse
from database import Request, get_async_session, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

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
    },
    3: {
        "title": "The Hobbit",
        "chapter": 4,
        "question": "Why did Bilbo leave home?"
    },
    4: {
        "title": "1984",
        "chapter": 3,
        "question": "Who is Big Brother?"
    },
    5: {
        "title": "The Great Gatsby",
        "chapter": 2,
        "question": "Who is Nick Carraway?"
    },
    6: {
        "title": "Pride and Prejudice",
        "chapter": 10,
        "question": "Why does Elizabeth dislike Mr. Darcy?"
    },
    7: {
        "title": "The Hunger Games",
        "chapter": 7,
        "question": "Who is Peeta?"
    },
    8: {
        "title": "The Fellowship of the Ring",
        "chapter": 5,
        "question": "What is special about Frodo's ring?"
    },
    9: {
        "title": "Percy Jackson and the Lightning Thief",
        "chapter": 8,
        "question": "Who is Percy's father?"
    },
    10: {
        "title": "Frankenstein",
        "chapter": 12,
        "question": "Why did Victor create the creature?"
    }
}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ask")
def get_all_requests():
    return book_requests

@app.get("/ask/{id}")
def get_request_by_id(id: int) -> AskResponse:
    return book_requests.get(id)

@app.post("/ask")
def ask_question(request: AskRequest) -> AskResponse :
    new_request = {
        "title": request.title,
        "chapter": request.chapter,
        "question": request.question
    }
    new_id = max(book_requests.keys()) + 1
    book_requests[new_id] = new_request
    return AskResponse(title=request.title, 
                       chapter=request.chapter, 
                       question=request.question, 
                       response="This is a spoiler free response!")