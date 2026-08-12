import { useState, useEffect } from 'react';
import AnswerCard from './AnswerCard';
import ReadingStatus from './ReadingStatus';

const BASEURL = 'http://localhost:8000/ask';
const BOOKS_URL = 'http://localhost:8000/books'
const QUESTIONS_URL = 'http://localhost:8000/questions'

function QuestionForm() {
  const [bookId, setBookId] = useState('');
  const [bookChapter, setBookChapter] = useState('');
  const [bookQuestion, setBookQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('idle');
  const [submittedBook, setSubmittedBook] = useState(null);
  const [books, setBooks] = useState([]);
  const [previousQuestions, setPreviousQuestions] = useState([]);

  useEffect(() => {
    async function fetchBooks() {
      try {
        const response = await fetch(BOOKS_URL);

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setBooks(data);
      } catch (error) {
        setError(error.message);
        setStatus('Error');
      }
  }
  fetchBooks();
  // fetch previous questions as well
  async function fetchPreviousQuestions() {
    try {
      const resp = await fetch(QUESTIONS_URL);
      if (!resp.ok) throw new Error(`HTTP error! Status: ${resp.status}`);
      const data = await resp.json();
      setPreviousQuestions(data.questions || []);
    } catch (err) {
      // don't block UI on questions failure
      console.warn('Failed to load previous questions', err);
    }
  }
  fetchPreviousQuestions();
}, []);

  const selectedBook = books.find(
  (book) => book.book_id === bookId
  );

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError(null);
    setAnswer('');
    setStatus('Loading');

    const chapterNumber = Number(bookChapter);
    const selectedBookTitle = books.find(
      (bookOption) => bookOption.book_id === bookId,
    )?.title;
    const book = {
      book_id: bookId,
      current_chapter: chapterNumber,
      question: bookQuestion,
    };

    try {
      const response = await fetch(BASEURL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(book),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

        const data = await response.json();
        setSubmittedBook({
          ...book,
          title: selectedBookTitle || '',
        });
        setAnswer(data.answer);
        setStatus("Success");
      }
        catch(error){
          setError(error.message);
          console.log(error.message);
          setStatus("Error");
        }
  };

  return (
    <div className="question-form-container">
      <form onSubmit={handleSubmit} className="question-form">
        <label className="form-label" htmlFor="book-title">
          Book title
        </label>

        <select
          className="form-input"
          id="book-title"
          value={bookId}
          onChange={(e) => {
            setBookId(e.target.value)
            setBookChapter('');
          }}
          required
        >
          <option value={""}>Select a book</option>
          {books.map((book) => (
            <option key={book.book_id} value={book.book_id}>
              {book.title}
            </option>
          ))}
        </select>
        <label className="form-label" htmlFor="book-chapter">
          Current chapter
        </label>

        <select
          className="form-input"
          id="book-chapter"
          value={bookChapter}
          onChange={(event) => setBookChapter(event.target.value)}
          disabled={!selectedBook}
          required
        >
          <option value="">Select a chapter</option>

          {selectedBook &&
            Array.from(
              { length: selectedBook.total_chapters },
              (_, index) => {
                const chapter = index + 1;

                return (
                  <option key={chapter} value={chapter}>
                    Chapter {chapter}
                  </option>
                );
              }
            )}
        </select>

        <label className="form-label" htmlFor="book-question">
          Question
        </label>
        <textarea
          className="form-textarea"
          id="book-question"
          value={bookQuestion}
          onChange={(e) => setBookQuestion(e.target.value)}
          required
        />
        {/* Inline suggestions: show previous questions matching the user's input */}
        {bookQuestion && previousQuestions.length > 0 && (
          (() => {
            const qLower = bookQuestion.toLowerCase();
            const suggestions = previousQuestions
              .filter((q) => q.question && q.question.toLowerCase().includes(qLower))
              .slice(0, 10);

            if (suggestions.length === 0) return null;

            return (
              <div className="suggestions" style={{ marginTop: 8 }}>
                <div className="suggestions-label">Previous questions</div>
                <ul className="suggestions-list" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {suggestions.map((s) => (
                    <li key={s.id} style={{ padding: '6px 8px', cursor: 'pointer' }} onClick={() => {
                      setBookId(s.book_id);
                      setBookChapter(String(s.current_chapter));
                      setBookQuestion(s.question);
                      setAnswer(s.answer || '');
                      setSubmittedBook({
                        book_id: s.book_id,
                        current_chapter: s.current_chapter,
                        title: books.find((b) => b.book_id === s.book_id)?.title || '',
                      });
                      setStatus('Success');
                    }}>
                      <strong>{books.find((b) => b.book_id === s.book_id)?.title || s.book_id}</strong>
                      {` — Ch ${s.current_chapter}: `}
                      <span>{s.question}</span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })()
        )}

        <button className="form-button" type="submit" disabled={status === "Loading"}>
          Submit
        </button>
      </form>

      {status === "Error" && error && <p className='error-message'>{error}</p>}
      {status === 'Loading' && <p className='loading-message'> Loading answer...</p>}
      {submittedBook && (
        <ReadingStatus
          bookTitle={submittedBook.title}
          currentChapter={submittedBook.current_chapter}
        />
      )}
      {status === 'Success' && answer && <AnswerCard answer={answer} />}
    </div>
  );
}

export default QuestionForm;