import { useState } from 'react';

export default function QuestionBox({ onAsk, loading }) {
  const [question, setQuestion] = useState('');

  function submit() {
    const q = question.trim();
    if (!q) return;
    onAsk(q);
  }

  return (
    <div className="card">
      <h2>2. Ask a question</h2>
      <textarea
        placeholder="What would you like to know about your documents?"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={loading}
      />
      <button onClick={submit} disabled={loading || !question.trim()}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>
    </div>
  );
}
