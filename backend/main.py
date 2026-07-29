from fastapi import FastAPI

from schemas import AskRequest, AskResponse

app = FastAPI()

book_questions = {
    1: {
        "book": "Dune",
        "chapter": 15,
        "question": "Who is Paul?"
    },
    2: {
        "book": "Harry Potter and the Philosopher's Stone",
        "chapter": 6,
        "question": "Who is Hagrid?"
    },
    3: {
        "book": "The Hobbit",
        "chapter": 4,
        "question": "Why did Bilbo leave home?"
    },
    4: {
        "book": "1984",
        "chapter": 3,
        "question": "Who is Big Brother?"
    },
    5: {
        "book": "The Great Gatsby",
        "chapter": 2,
        "question": "Who is Nick Carraway?"
    },
    6: {
        "book": "Pride and Prejudice",
        "chapter": 10,
        "question": "Why does Elizabeth dislike Mr. Darcy?"
    },
    7: {
        "book": "The Hunger Games",
        "chapter": 7,
        "question": "Who is Peeta?"
    },
    8: {
        "book": "The Fellowship of the Ring",
        "chapter": 5,
        "question": "What is special about Frodo's ring?"
    },
    9: {
        "book": "Percy Jackson and the Lightning Thief",
        "chapter": 8,
        "question": "Who is Percy's father?"
    },
    10: {
        "book": "Frankenstein",
        "chapter": 12,
        "question": "Why did Victor create the creature?"
    }
}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ask")
def get_all_requests():
    return book_questions

@app.get("/ask/{id}")
def get_request_by_id(id: int) -> AskResponse:
    return book_questions.get(id)

@app.post("/ask")
def ask_question(question: AskRequest) -> AskResponse :
    new_request = {
        "book": question.book,
        "chapter": question.chapter,
        "question": question.question
    }
    new_id = max(book_questions.keys()) + 1
    book_questions[new_id] = new_request
    return new_request