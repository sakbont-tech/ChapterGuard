from fastapi.testclient import TestClient
from dotenv import load_dotenv
load_dotenv()
from backend.main import app

client = TestClient(app)

payload = {
    "book_id": "count_of_monte_cristo",
    "current_chapter": 14,
    "question": "Who is Edmond Dantès?",
}

response = client.post("/ask", json=payload)
print('status', response.status_code)
print('text', response.text)
try:
    print('json', response.json())
except Exception as e:
    print('json parse error', e)
