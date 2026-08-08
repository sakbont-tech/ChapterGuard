import { useState, useEffect } from 'react';
import AnswerCard from './AnswerCard';
import ReadingStatus from './ReadingStatus';

const BASEURL = 'http://localhost:8000/ask';
const BOOKS_URL = 'http://localhost:8000/books'

function QuestionForm() {
  const [bookId, setBookId] = useState('');
  const [bookChapter, setBookChapter] = useState('');
  const [bookQuestion, setBookQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('idle');
  const [submittedBook, setSubmittedBook] = useState(null);
  const [books, setBooks] = useState([]);

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
        setSubmittedBook(book);
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
          {books.map((book) => {
            <option key={book.book_id} value={book.book_id}>
              {book.title}
            </option>
          })}
        </select>
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

        <button className="form-button" type="submit" disabled={status === "Loading"}>
          Submit
        </button>
      </form>

      {status === "Error" && error && <p className='error-message'>{error}</p>}
      {status === 'Loading' && <p className='loading-message'> Loading answer...</p>}
      {submittedBook && (
        <ReadingStatus
          bookId={submittedBook.title}
          currentChapter={submittedBook.chapter}
        />
      )}
      {status === 'Success' && answer && <AnswerCard answer={answer} />}
    </div>
  );
}

export default QuestionForm;