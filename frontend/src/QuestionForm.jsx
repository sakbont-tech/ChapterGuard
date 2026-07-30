import { useState } from 'react';
import AnswerCard from './AnswerCard';
import ReadingStatus from './ReadingStatus';

const BASEURL = 'http://localhost:8000/ask';

function QuestionForm() {
  const [bookTitle, setBookTitle] = useState('');
  const [bookChapter, setBookChapter] = useState('');
  const [bookQuestion, setBookQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('idle');
  const [submittedBook, setSubmittedBook] = useState(null);

  
  const handleSubmit = async (event) => {
    event.preventDefault();

    setError(null);
    setAnswer('');
    setStatus('Loading');

    const chapterNumber = Number(bookChapter);
    const book = {
      title: bookTitle, 
      chapter: chapterNumber,
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
        setAnswer(data.response);
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
        <input
          className="form-input"
          id="book-title"
          type="text"
          value={bookTitle}
          onChange={(e) => setBookTitle(e.target.value)}
          placeholder="Enter Book Title"
          required
        />

        <label className="form-label" htmlFor="book-chapter">
          Current chapter
        </label>
        <input
          className="form-input"
          id="book-chapter"
          type="number"
          value={bookChapter}
          onChange={(e) => setBookChapter(e.target.value)}
          min="1"
          required
        />

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
          bookTitle={submittedBook.title}
          currentChapter={submittedBook.chapter}
        />
      )}
      {status === 'Success' && answer && <AnswerCard answer={answer} />}
    </div>
  );
}

export default QuestionForm;