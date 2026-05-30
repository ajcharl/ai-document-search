export default function AnswerDisplay({ answer, sources, loading, error }) {
  if (!loading && !answer && !error) return null;

  return (
    <div className="card">
      <h2>3. Answer</h2>
      {loading && <div className="status">Retrieving relevant chunks and querying Mistral...</div>}
      {error && <div className="status error">{error}</div>}
      {answer && <div className="answer">{answer}</div>}
      {sources && sources.length > 0 && (
        <>
          <h2 style={{ marginTop: 16 }}>Sources</h2>
          <div className="sources">
            {sources.map((s, i) => (
              <div className="source" key={i}>
                <div className="source-meta">{s.source}</div>
                <div>{s.snippet}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
