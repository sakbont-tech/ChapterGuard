import {useState} from 'react';

function QuestionForm(){

    const [bookTitle, setBookTitle] = useState("");
    const [bookChapter, setBookChapter] = useState("");
    const [bookQuestion, setBookQuestion] = useState("");
    const [answer, setAnswer] = useState("");

    const handleBookTitleChange = (event) =>{
        setBookTitle(event.target.value);
    };
    
    const handleBookChapterChange = (event) =>{
        setBookChapter(event.target.value);
    };

    const handleBookQuestionChange = (event) =>{
        setBookQuestion(event.target.value);
    };

    const handleSubmit = (event) =>{
        event.preventDefault();

        let chapterNumber = Number(bookChapter);

        console.log({
            title: bookTitle,
            chapter: chapterNumber,
            question: bookQuestion
        });

        setAnswer("Spoiler Free Zone");
    }

    return(
        <div className="Question-Form-Container">
            <form onSubmit={handleSubmit}>

                <label htmlFor="book-title">Book title</label>
                <input id='book-title' 
                       type='text' 
                       value={bookTitle} 
                       onChange={handleBookTitleChange}
                       placeholder='Enter Book Title'
                       required
                />

                <label htmlFor="book-chapter">Current chapter</label>
                <input id='book-chapter' 
                       type='number' 
                       value={bookChapter} 
                       onChange={handleBookChapterChange}
                       min='1'
                       required
                />

                <label htmlFor="book-question">Question</label>
                <textarea id='book-question' 
                       type='text' 
                       value={bookQuestion} 
                       onChange={handleBookQuestionChange}
                       required
                />

                <button type='submit'>Submit</button>
            </form>

            {answer && <p>{answer}</p>}
        </div>


    );

}
export default QuestionForm