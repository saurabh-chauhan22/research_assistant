import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { search } from '../services/api';
import './chat.css';

export default function Chat() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    setAnswer(null);
    setSources([]);
    setError(null);
    setLoading(true);

    try {
      const data = await search(trimmed);
      if (data.error) {
        setError(data.error);
        setAnswer(data.final_output || null);
      } else {
        setAnswer(data.final_output ?? '');
        setSources(Array.isArray(data.sources) ? data.sources : []);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center py-5 px-3 bg-light">
      <div className="container py-4">
        <div className="text-center mb-4">
          <h1 className="display-5 fw-bold text-primary mb-2">Research Assistant</h1>
          <p className="lead text-muted">Ask a question and get a research-backed answer.</p>
        </div>

        <form onSubmit={handleSubmit} className="row justify-content-center">
          <div className="col-12 col-lg-8 col-xl-7">
            <div className="input-group input-group-lg shadow-sm">
              <input
                type="text"
                className="form-control form-control-lg border-primary"
                placeholder="Enter your research question..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
                autoFocus
                aria-label="Research question"
              />
              <button
                type="submit"
                className="btn btn-primary px-4"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                    Searching…
                  </>
                ) : (
                  'Search'
                )}
              </button>
            </div>
          </div>
        </form>

        {loading && (
          <div className="row justify-content-center mt-4">
            <div className="col-12 col-lg-8 col-xl-7">
              <div className="card border-0 shadow-sm">
                <div className="card-body d-flex align-items-center gap-3 py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading…</span>
                  </div>
                  <p className="mb-0 text-muted">Searching and analyzing sources…</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {!loading && (answer !== null || error) && (
          <div className="row justify-content-center mt-4">
            <div className="col-12 col-lg-8 col-xl-7">
              <div className="card border-0 shadow-sm">
                <div className="card-body p-4">
                  {error && (
                    <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                      <span className="me-2">⚠</span>
                      {error}
                    </div>
                  )}
                  {answer !== null && answer !== '' && (
                    <>
                      <h5 className="card-title text-primary mb-3">Answer</h5>
                      <div className="answer-markdown card-text mb-0">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
                      </div>
                      {sources.length > 0 && (
                        <div className="sources-section mt-4 pt-3 border-top">
                          <h6 className="fw-bold text-primary mb-3">Sources</h6>
                          <ol className="sources-list mb-0 ps-3">
                            {sources.map((src, idx) => (
                              <li key={idx} className="mb-2">
                                <a
                                  href={src.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="source-link"
                                >
                                  {src.title || 'Unknown'}
                                </a>
                                <span className="text-muted small ms-1"> — {src.url}</span>
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
