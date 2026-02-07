import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { createClient } from "@supabase/supabase-js";

const SAMPLES = [
  { label: "DB error", source: "backend", log: "psql: connection refused" },
  { label: "Timeout", source: "ci", log: "Request timed out after 30s, retry attempt 2" },
  { label: "Auth", source: "nginx", log: "403 Forbidden: permission denied" },
  { label: "Config", source: "k8s", log: "invalid config: missing API_KEY" },
];

const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

export default function App() {
  const [log, setLog] = useState("");
  const [source, setSource] = useState("ci");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState("");

  const canAnalyze = useMemo(() => log.trim().length >= 5 && !loading, [log, loading]);
  const canSave = useMemo(() => !!result && !!supabase && !saving, [result, saving]);

  async function refreshHistory() {
    setHistoryError("");
    if (!supabase) return;
    try {
      const { data, error } = await supabase
        .from("incident_events")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(20);

      if (error) throw error;
      setHistory(data || []);
    } catch (e) {
      setHistoryError(e?.message || "Failed to load history");
    }
  }

  useEffect(() => {
    refreshHistory();
  }, []);

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

  async function onSave() {
    if (!supabase || !result) return;
    setSaving(true);
    setError("");
    try {
      const payload = {
        source,
        log,
        incident_type: result.incident_type,
        severity: result.severity,
        team: result.team,
        confidence: Number(result.confidence),
        action: result.action,
      };

      const { error } = await supabase.from("incident_events").insert(payload);
      if (error) throw error;

      await refreshHistory();
    } catch (e) {
      setError(e?.message || "Failed to save incident");
    } finally {
      setSaving(false);
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
            <button className="btn" onClick={onSave} disabled={!canSave}>
              {saving ? "Saving..." : supabase ? "Save to History" : "DB not configured"}
            </button>
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

        <section className="card" style={{ gridColumn: "1 / -1" }}>
          <div className="cardTitle">History (Supabase)</div>
          {!supabase && (
            <div className="empty">
              Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code> in <code>.env.local</code>.
            </div>
          )}
          {historyError && <div className="alert"><strong>Error:</strong> {historyError}</div>}
          {supabase && (
            <div style={{ overflow: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ textAlign: "left", color: "rgba(255,255,255,0.7)" }}>
                    <th style={{ padding: 10 }}>Time</th>
                    <th style={{ padding: 10 }}>Source</th>
                    <th style={{ padding: 10 }}>Type</th>
                    <th style={{ padding: 10 }}>Severity</th>
                    <th style={{ padding: 10 }}>Team</th>
                    <th style={{ padding: 10 }}>Conf</th>
                    <th style={{ padding: 10 }}>Log</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h) => (
                    <tr key={h.id} style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
                      <td style={{ padding: 10, whiteSpace: "nowrap" }}>{new Date(h.created_at).toLocaleString()}</td>
                      <td style={{ padding: 10 }}>{h.source}</td>
                      <td style={{ padding: 10 }}>{h.incident_type}</td>
                      <td style={{ padding: 10 }}>{h.severity}</td>
                      <td style={{ padding: 10 }}>{h.team}</td>
                      <td style={{ padding: 10 }}>{Number(h.confidence).toFixed(2)}</td>
                      <td style={{ padding: 10, minWidth: 360 }}>{h.log}</td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td style={{ padding: 10 }} colSpan={7} className="empty">
                        No saved incidents yet. Run “Analyze” then “Save to History”.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
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
