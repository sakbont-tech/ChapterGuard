import Markdown from 'react-markdown'

function AnswerCard({ answer }) {
  return (
    <div className="answer-card">
      <Markdown>{answer}</Markdown>
    </div>
  );
}

export default AnswerCard;