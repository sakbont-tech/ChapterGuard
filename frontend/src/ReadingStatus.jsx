function ReadingStatus({ bookTitle, currentChapter }) {
  return (
    <div className="reading-status">
      <p>Book Title: {bookTitle}</p>
      <p>Current Chapter: {currentChapter}</p>
    </div>
  );
}

export default ReadingStatus;
