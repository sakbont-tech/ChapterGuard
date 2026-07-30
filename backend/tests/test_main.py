from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_ask_returns_response_for_valid_request():
    payload = {
        "title": "A Game of Thrones",
        "chapter": 14,
        "question": "Who is Ned Stark?"
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "title": "A Game of Thrones",
        "chapter": 14,
        "question": "Who is Ned Stark?",
        "response": "This is a spoiler free response!"
    }


def test_post_ask_rejects_chapter_zero():
    payload = {
        "title": "A Game of Thrones",
        "chapter": 0,
        "question": "Who is Ned Stark?"
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422


def test_post_ask_rejects_null_question():
    payload = {
        "title": "A Game of Thrones",
        "chapter": 14,
        "question": None
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422

def test_post_ask_rejects_missing_title():
    payload = {
        "chapter": 14,
        "question": "Who is Ned Stark?"
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422