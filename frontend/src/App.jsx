import { useState } from 'react';
import FileUpload from './components/FileUpload.jsx';
import QuestionBox from './components/QuestionBox.jsx';
import AnswerDisplay from './components/AnswerDisplay.jsx';

export default function App() {
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState('');

  async function handleAsk(question) {
    setAsking(true);
    setAskError('');
    setAnswer(null);
    setSources([]);
    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Request failed');
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      setAskError(err.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app">
      <h1>RAG Document Search</h1>
      <p className="subtitle">
        Upload PDF or TXT documents, then ask questions answered only from their contents.
      </p>

      <FileUpload />
      <QuestionBox onAsk={handleAsk} loading={asking} />
      <AnswerDisplay answer={answer} sources={sources} loading={asking} error={askError} />
    </div>
  );
}
