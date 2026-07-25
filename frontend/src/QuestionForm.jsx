import {useState} from 'react';

function QuestionForm(){

    const [bookTitle, setBookTitle] = useState("");
    const [bookChapter, setBookChapter] = useState("");
    const [bookQuestion, setBookQuestion] = useState("");

    const handleBookTitleChange = (event) =>{
        setBookTitle(event.target.value);
    };
    
    const handleBookChapterChange = (event) =>{
        setBookChapter(event.target.value);
    };

    const handleBookQuestionChange = (event) =>{
        setBookQuestion(event.target.value);
    };

    return(
        <div className="Question-Form-Container">
            <form>

                <label htmlFor="book-title">Book title</label>
                <input id='Book-Title' 
                       type='text' 
                       value={bookTitle} 
                       onChange={handleBookTitleChange}
                       placeholder='Enter Book Title'
                       required
                />

                <label htmlFor="book-chapter">Current chapter</label>
                <input id='Book-Chapter' 
                       type='number' 
                       value={bookChapter} 
                       onChange={handleBookChapterChange}
                       min='1'
                       required
                />

                <label htmlFor="book-question">Question</label>
                <textarea id='Book-Question' 
                       type='text' 
                       value={bookQuestion} 
                       onChange={handleBookQuestionChange}
                       required
                />
            </form>
        </div>
    );

}
export default QuestionForm