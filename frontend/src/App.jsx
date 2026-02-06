import { useMemo, useState } from "react";
import "./App.css";

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

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "system-ui, Arial" }}>
      <h1 style={{ marginBottom: 6 }}>Incident Decision Engine</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Paste a log line or error message. The system returns a deterministic incident decision.
      </p>

      <div style={{ display: "grid", gap: 12 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontWeight: 600 }}>Source</span>
          <select value={source} onChange={(e) => setSource(e.target.value)} style={{ padding: 10 }}>
            <option value="ci">CI</option>
            <option value="backend">Backend</option>
            <option value="nginx">Nginx</option>
            <option value="k8s">Kubernetes</option>
          </select>
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontWeight: 600 }}>Log / Error</span>
          <textarea
            value={log}
            onChange={(e) => setLog(e.target.value)}
            rows={8}
            placeholder="e.g. psql: connection refused"
            style={{ padding: 12, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}
          />
        </label>

        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <button
            onClick={onAnalyze}
            disabled={!canAnalyze}
            style={{
              padding: "10px 16px",
              cursor: canAnalyze ? "pointer" : "not-allowed",
              fontWeight: 700,
            }}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>

          <span style={{ opacity: 0.7 }}>
            API: <code>{apiBase}</code>
          </span>
        </div>

        {error && (
          <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 10 }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 10 }}>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
              <Badge label={`Type: ${result.incident_type}`} />
              <Badge label={`Severity: ${result.severity}`} />
              <Badge label={`Team: ${result.team}`} />
              <Badge label={`Confidence: ${Number(result.confidence).toFixed(2)}`} />
            </div>

            <div style={{ marginBottom: 10 }}>
              <div style={{ fontWeight: 700, marginBottom: 6 }}>Recommended action</div>
              <div>{result.action}</div>
            </div>

            <details>
              <summary style={{ cursor: "pointer" }}>Raw JSON</summary>
              <pre style={{ overflow: "auto", paddingTop: 10 }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

function Badge({ label }) {
  return (
    <span
      style={{
        display: "inline-flex",
        padding: "6px 10px",
        border: "1px solid #ddd",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 700,
      }}
    >
      {label}
    </span>
  );
}

