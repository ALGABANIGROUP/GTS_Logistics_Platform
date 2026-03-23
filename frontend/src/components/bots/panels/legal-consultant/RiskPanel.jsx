import { useState } from "react";

// Placeholder UI: risk endpoints are part of review results and advisory; this view organizes summaries.
export default function RiskPanel({ service, disabled }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    const res = await service.reviewHistory({ limit: 20, offset: 0 });
    setHistory(res);
    setLoading(false);
  };

  return (
    <div className="lc-card">
      <div className="lc-section-title">Risk Insights</div>
      <div className="lc-actions">
        <button onClick={loadHistory} disabled={disabled || loading}>
          {loading ? "Loading..." : "Load Recent Reviews"}
        </button>
      </div>
      {history ? (
        <pre className="lc-pre">{JSON.stringify(history, null, 2)}</pre>
      ) : (
        <div className="lc-muted">No data loaded yet.</div>
      )}
    </div>
  );
}
