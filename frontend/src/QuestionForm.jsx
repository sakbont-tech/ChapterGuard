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
          <label className="form-label" htmlFor="previous-question">
            Previous questions
          </label>
          <select
            className="form-input"
            id="previous-question"
            value={""}
            onChange={(e) => {
              const id = e.target.value;
              if (!id) return;
              const selected = previousQuestions.find((q) => q.id === id);
              if (!selected) return;
              // populate form with selected previous question
              setBookId(selected.book_id);
              setBookChapter(String(selected.current_chapter));
              setBookQuestion(selected.question);
              setAnswer(selected.answer || '');
              setSubmittedBook({
                book_id: selected.book_id,
                current_chapter: selected.current_chapter,
                title: books.find((b) => b.book_id === selected.book_id)?.title || '',
              });
              setStatus('Success');
            }}
          >
            <option value="">Select a previous question</option>
            {previousQuestions.map((q) => (
              <option key={q.id} value={q.id}>
                {`${books.find((b) => b.book_id === q.book_id)?.title || q.book_id} — Ch ${q.current_chapter}: ${q.question.slice(0,60)}`}
              </option>
            ))}
          </select>
        <textarea
          className="form-textarea"
          id="book-question"
          value={bookQuestion}
          onChange={(e) => setBookQuestion(e.target.value)}
          required
        />

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