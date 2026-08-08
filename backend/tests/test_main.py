from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_ask_returns_response_for_valid_request():
    payload = {
        "book_id": "count_of_monte_cristo",
        "current_chapter": 14,
        "question": "Who is Edmond Dantès?",
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "book_id": "count_of_monte_cristo",
        "current_chapter": 14,
        "question": "Who is Edmond Dantès?",
        "answer": "This is a spoiler free response!",
    }


def test_post_ask_rejects_chapter_zero():
    payload = {
        "book_id": "count_of_monte_cristo",
        "current_chapter": 0,
        "question": "Who is Edmond Dantès?",
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422


def test_post_ask_rejects_null_question():
    payload = {
        "book_id": "count_of_monte_cristo",
        "current_chapter": 14,
        "question": None,
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422


def test_post_ask_rejects_missing_book_id():
    payload = {
        "current_chapter": 14,
        "question": "Who is Edmond Dantès?",
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422

def test_get_books():

    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == [
        {
            "book_id": "count_of_monte_cristo",
            "title": "The Count of Monte Cristo",
            "total_chapters": 117
        }
    ]
