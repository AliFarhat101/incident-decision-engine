import { useMemo, useState } from "react";
import "./App.css";

const SAMPLES = [
  { label: "DB error", source: "backend", log: "psql: connection refused" },
  { label: "Timeout", source: "ci", log: "Request timed out after 30s, retry attempt 2" },
  { label: "Auth", source: "nginx", log: "403 Forbidden: permission denied" },
  { label: "Config", source: "k8s", log: "invalid config: missing API_KEY" },
];

export default function App() {
  const [log, setLog] = useState("");
  const [source, setSource] = useState("ci");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const canAnalyze = useMemo(() => log.trim().length >= 5 && !loading, [log, loading]);

  async function onAnalyze() {
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log, source }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API error ${res.status}: ${text}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function useSample(s) {
    setSource(s.source);
    setLog(s.log);
    setResult(null);
    setError("");
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1 className="title">Incident Decision Engine</h1>
          <p className="subtitle">
            Paste a log line or error message. Get a structured, automation-ready incident decision.
          </p>
        </div>
        <div className="pill">
          API <code className="code">{apiBase}</code>
        </div>
      </header>

      <main className="grid">
        <section className="card">
          <div className="cardTitle">Input</div>

          <div className="row">
            <label className="label">
              <span>Source</span>
              <select className="select" value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="ci">CI</option>
                <option value="backend">Backend</option>
                <option value="nginx">Nginx</option>
                <option value="k8s">Kubernetes</option>
              </select>
            </label>

            <div className="label">
              <span>Demo samples</span>
              <div className="samples">
                {SAMPLES.map((s) => (
                  <button key={s.label} className="chip" onClick={() => useSample(s)} type="button">
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <label className="label">
            <span>Log / Error</span>
            <textarea
              className="textarea"
              value={log}
              onChange={(e) => setLog(e.target.value)}
              rows={10}
              placeholder="e.g. psql: connection refused"
            />
          </label>

          <div className="actions">
            <button className="btn" onClick={onAnalyze} disabled={!canAnalyze}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
            <div className="hint">Tip: use a demo sample for quick screenshots.</div>
          </div>

          {error && (
            <div className="alert">
              <strong>Error:</strong> {error}
            </div>
          )}
        </section>

        <section className="card">
          <div className="cardTitle">Decision</div>

          {!result ? (
            <div className="empty">
              {loading ? "Waiting for response…" : "Run an analysis to see the incident decision."}
            </div>
          ) : (
            <>
              <div className="badges">
                <Badge label={`Type: ${result.incident_type}`} />
                <Badge label={`Severity: ${result.severity}`} />
                <Badge label={`Team: ${result.team}`} />
                <Badge label={`Confidence: ${Number(result.confidence).toFixed(2)}`} />
              </div>

              <div className="block">
                <div className="blockTitle">Recommended action</div>
                <div className="blockBody">{result.action}</div>
              </div>

              <details className="details">
                <summary>Raw JSON</summary>
                <pre className="pre">{JSON.stringify(result, null, 2)}</pre>
              </details>
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>v1 • deterministic decisions • ML-backed classification</span>
      </footer>
    </div>
  );
}

function Badge({ label }) {
  return <span className="badge">{label}</span>;
}
