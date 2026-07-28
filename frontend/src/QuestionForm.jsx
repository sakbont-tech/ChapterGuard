import { useState } from 'react';
import AnswerCard from './AnswerCard';
import ReadingStatus from './ReadingStatus';

function QuestionForm() {
  const [bookTitle, setBookTitle] = useState('');
  const [bookChapter, setBookChapter] = useState('');
  const [bookQuestion, setBookQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [state, setState] = useState('');
  const [submittedBook, setSubmittedBook] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();

    const chapterNumber = Number(bookChapter);
    const book = {
      title: bookTitle, 
      chapter: chapterNumber,
      question: bookQuestion,
    };

    setSubmittedBook(book);
    setState('Loading');

    setTimeout(() => {
      setState('Answering');
      setAnswer('Spoiler Free Zone');
    }, 2000);
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

        <button className="form-button" type="submit">
          Submit
        </button>
      </form>

      {state === 'Loading' && <p>Loading answer...</p>}
      {submittedBook && (
        <ReadingStatus
          bookTitle={submittedBook.title}
          currentChapter={submittedBook.chapter}
        />
      )}
      {state === 'Answering' && answer && <AnswerCard answer={answer} />}
    </div>
  );
}

export default QuestionForm;
