# ChapterGuard

readme_content = """# ChapterGuard 🛡️📖

**ChapterGuard** is an AI-powered reading companion designed to answer your questions about a book without ever spoiling what happens next.

Ever forgot who a character was in chapter 15, but were too afraid to Google them because the search results would reveal their death in chapter 40? ChapterGuard solves this. By feeding a Large Language Model (LLM) the text of a public domain book _strictly up to your current chapter_, it guarantees that the AI physically does not know the future of the plot, ensuring 100% spoiler-free answers.

## ✨ Features

- **Spoiler-Free AI Responses:** Powered by Google's Gemini 1.5 Flash model, strictly prompted and context-limited to prevent plot leaks.
- **Smart Context Loading:** Automatically compiles and processes raw book text up to the user's specified chapter.
- **Persistent Chat History:** Questions and AI answers are securely saved in a local SQLite database, allowing users to view their past inquiries via a UI dropdown.
- **Modern Stack:** A fast, asynchronous Python backend communicating with a responsive React frontend.

## 🛠️ Tech Stack

**Frontend:**

- React (via Vite)
- Standard CSS

**Backend:**

- Python 3.x
- FastAPI (Asynchronous API framework)
- SQLAlchemy & `aiosqlite` (Async Database ORM)
- Google GenAI SDK (`gemini-1.5-flash`)
- Pytest (Automated Testing)

---

## 🚀 Local Development Setup

To run ChapterGuard on your local machine, you will need two terminal windows: one for the Python backend and one for the React frontend.

### Prerequisites

- [Node.js](https://nodejs.org/) installed for the frontend.
- [Python 3.10+](https://www.python.org/) installed for the backend.
- A free [Google Gemini API Key](https://aistudio.google.com/).

### 1. Backend Setup

Open your terminal and navigate to the root directory of the project, then into the backend folder:

```bash
cd backend
```

#### Create a Virtual Environment

Create and activate a Python virtual environment:

```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

#### Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `backend` directory with the following variables:

```
GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./chapterguard.db
```

Replace `your_gemini_api_key_here` with your actual Google Gemini API key.

#### Run the Backend Server

Start the FastAPI server:

```bash
python main.py
```

The backend will run on `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
```

#### Install Dependencies

Install Node.js dependencies:

```bash
npm install
```

#### Run the Development Server

Start the Vite development server:

```bash
npm run dev
```

The frontend will typically run on `http://localhost:5173`. Open this URL in your browser.

---

## 📁 Project Structure

```
ChapterGuard/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Application entry point
│   ├── database.py            # Database configuration & models
│   ├── book_loader.py         # Book text processing & chapter extraction
│   ├── schemas.py             # Pydantic request/response models
│   ├── requirements.txt        # Python dependencies
│   ├── data/
│   │   └── books/             # Local book storage
│   │       └── count_of_monte_cristo/
│   │           ├── metadata.json
│   │           ├── raw.txt
│   │           └── chapters/
│   └── tests/                 # Pytest test suite
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx            # Main application component
│   │   ├── QuestionForm.jsx   # Question input component
│   │   ├── AnswerCard.jsx     # Answer display component
│   │   ├── ReadingStatus.jsx  # Reading progress component
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   └── vitest.config.js       # Vitest configuration for unit tests
│
└── README.md                  # This file
```

---

## 🎯 How to Use ChapterGuard

1. **Load a Book:** The application comes pre-configured with "The Count of Monte Cristo". Specify which chapter you're currently reading.
2. **Ask Questions:** Type any question about the book in the question form.
3. **Get Spoiler-Free Answers:** The AI will answer based only on the chapters you've read.
4. **View History:** Access your past questions and answers from the chat history dropdown.

---

## 🔌 API Endpoints

The backend provides the following REST API endpoints:

### Questions

- `POST /api/ask` - Submit a question about the current book
  - **Body:** `{ "question": "string", "book_id": "string", "chapter": "number" }`
  - **Response:** `{ "answer": "string", "history_id": "number" }`

- `GET /api/history/{book_id}` - Get chat history for a book
  - **Response:** List of past questions and answers

### Books

- `GET /api/books` - Get available books
- `GET /api/books/{book_id}/chapters` - Get chapter list and metadata

---

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

### Backend Tests

```bash
cd backend
pytest
```

Pytest automatically discovers and runs all tests in the `tests/` directory.

### Frontend Tests

```bash
cd frontend
npm run test
```

Vitest runs unit and component tests for React components.

---

## 🔑 Environment Variables Reference

| Variable         | Description                       | Example                       |
| ---------------- | --------------------------------- | ----------------------------- |
| `GOOGLE_API_KEY` | Your Google Gemini API key        | `AIzaSyD...`                  |
| `DATABASE_URL`   | SQLite database connection string | `sqlite:///./chapterguard.db` |
| `BACKEND_URL`    | Backend server URL (frontend)     | `http://localhost:8000`       |

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** "ModuleNotFoundError: No module named 'fastapi'"

- **Solution:** Ensure you've activated the virtual environment and run `pip install -r requirements.txt`

**Problem:** "GOOGLE_API_KEY not found"

- **Solution:** Create a `.env` file in the `backend` directory with your API key

**Problem:** Database errors on startup

- **Solution:** Delete `chapterguard.db` and restart the server to reinitialize the database

### Frontend Issues

**Problem:** "Cannot find module 'react'"

- **Solution:** Run `npm install` in the frontend directory

**Problem:** Backend requests fail with CORS error

- **Solution:** Ensure the backend is running on `http://localhost:8000`

---

## 📝 Adding New Books

To add a new book to ChapterGuard:

1. Create a new folder under `backend/data/books/{book_name}/`
2. Add the raw book text as `raw.txt`
3. Create a `metadata.json` file with book information:
   ```json
   {
     "title": "Book Title",
     "author": "Author Name",
     "total_chapters": 50,
     "description": "Book description"
   }
   ```
4. Run the `scripts/split_book.py` script to generate chapter files

**Happy reading with ChapterGuard! 🛡️📖**
