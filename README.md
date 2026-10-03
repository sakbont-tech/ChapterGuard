# ChapterGuard

ChapterGuard is an AI reading companion that answers questions about a book using only the chapters the reader has reached. The application limits the context sent to Google Gemini so that answers are grounded in the selected portion of the story.

The current MVP supports **The Count of Monte Cristo** by Alexandre Dumas.

## Features

- Select the last chapter you have reached
- Ask questions about characters, events, and details from the story
- Restrict Gemini's context to Chapters 1 through the selected chapter
- Render formatted AI responses in a React interface
- Store previous questions and answers in SQLite
- Retrieve question history through the backend API
- Test backend and frontend behaviour with Pytest, Vitest, and React Testing Library
- Run automated tests with GitHub Actions

## How it works

1. The included public domain text is split into 117 chapter files.
2. The React frontend retrieves the supported book and chapter count from FastAPI.
3. The reader selects a chapter and submits a question.
4. The backend loads the text from Chapter 1 through the selected chapter.
5. That text and the question are sent to Gemini with spoiler prevention instructions.
6. The answer is returned to the frontend and the exchange is saved in SQLite.

ChapterGuard reduces spoiler exposure by withholding later chapter text from the model. Model responses can still be imperfect, so this should be treated as a reading aid rather than a guarantee.

## Technology

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI |
| Frontend | React, Vite, JavaScript |
| AI | Google Gemini API |
| Database | SQLite, SQLAlchemy |
| Backend testing | Pytest, FastAPI TestClient |
| Frontend testing | Vitest, React Testing Library |
| Automation | GitHub Actions |

## Project structure

```text
ChapterGuard/
├── backend/
│   ├── data/books/              # Book metadata and source text
│   ├── scripts/split_book.py    # Generates individual chapter files
│   ├── tests/                   # Backend tests
│   ├── book_loader.py           # Loads metadata and chapter context
│   ├── database.py              # SQLAlchemy models and async sessions
│   ├── main.py                  # FastAPI application and routes
│   └── schemas.py               # Request and response models
├── frontend/
│   └── src/                     # React components and tests
└── .github/workflows/tests.yml  # Continuous integration
```

## Local setup

### Prerequisites

- Python 3.12 or a compatible Python 3 version
- Node.js 24 or a compatible modern Node.js version
- A [Google Gemini API key](https://aistudio.google.com/)

### 1. Clone the repository

```bash
git clone https://github.com/sakbont-tech/ChapterGuard.git
cd ChapterGuard
```

### 2. Set up the backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Generate the chapter files from the included public domain source text:

```bash
python backend/scripts/split_book.py
```

The generated chapter files are intentionally excluded from Git because they can be reproduced from `raw.txt`.

Start the backend from the repository root:

```bash
python -m uvicorn backend.main:app --reload
```

The API runs at [http://localhost:8000](http://localhost:8000), with interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL displayed by Vite, normally [http://localhost:5173](http://localhost:5173).

## Using ChapterGuard

1. Select **The Count of Monte Cristo**.
2. Select the last chapter you have read.
3. Enter a question about the story.
4. Submit the form and wait for the Gemini response.

The selected chapter is included in the allowed context. Selecting Chapter 14 gives Gemini access to Chapters 1 through 14.

## API

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### List supported books

```http
GET /books
```

Response:

```json
[
  {
    "book_id": "count_of_monte_cristo",
    "title": "The Count of Monte Cristo",
    "total_chapters": 117
  }
]
```

### Ask a question

```http
POST /ask
Content-Type: application/json
```

Request:

```json
{
  "book_id": "count_of_monte_cristo",
  "current_chapter": 14,
  "question": "Who is Edmond Dantès?"
}
```

Response:

```json
{
  "book_id": "count_of_monte_cristo",
  "current_chapter": 14,
  "question": "Who is Edmond Dantès?",
  "answer": "..."
}
```

### Retrieve question history

```http
GET /questions
```

Response:

```json
{
  "questions": [
    {
      "id": "...",
      "book_id": "count_of_monte_cristo",
      "current_chapter": 14,
      "question": "Who is Edmond Dantès?",
      "answer": "..."
    }
  ]
}
```

## Testing

Generate the chapters before running the backend suite:

```bash
python backend/scripts/split_book.py
python -m pytest -q
```

Run the frontend suite:

```bash
cd frontend
npm run test -- --run
```

GitHub Actions runs both suites for pushes and pull requests targeting `main`.

## Current scope

ChapterGuard is a completed single-book MVP. It currently:

- Supports The Count of Monte Cristo
- Uses locally generated text files for chapter content
- Stores question history in a local SQLite database
- Runs as a local development application
- Has no user accounts or cloud deployment

The source text is from [Project Gutenberg](https://www.gutenberg.org/ebooks/1184).
