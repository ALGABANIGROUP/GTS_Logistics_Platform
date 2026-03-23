import { useState } from "react";

// This panel calls the AI-bot generic interface so users can ask legal questions via AIBotPage too.
// Here, we stick to compliance helpers and show bot status.
export default function AdvisoryPanel({ service, disabled }) {
  const [keywords, setKeywords] = useState("freight, shipping, logistics");
  const [monitor, setMonitor] = useState(null);
  const [status, setStatus] = useState(null);

  const runMonitor = async () => {
    const list = keywords
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const res = await service.monitorChanges({ keywords: list });
    setMonitor(res);
  };

  const loadStatus = async () => {
    const res = await service.botStatus();
    setStatus(res);
  };

  return (
    <div className="lc-col">
      <div className="lc-card">
        <div className="lc-section-title">Advisory Tools</div>
        <div className="lc-field">
          <label>Monitor Keywords</label>
          <input value={keywords} onChange={(e) => setKeywords(e.target.value)} />
        </div>
        <div className="lc-actions">
          <button onClick={runMonitor} disabled={disabled}>Monitor Changes</button>
          <button onClick={loadStatus} disabled={disabled}>Load Bot Status</button>
        </div>
      </div>

      {monitor ? (
        <div className="lc-card">
          <div className="lc-section-title">Monitoring</div>
          <pre className="lc-pre">{JSON.stringify(monitor, null, 2)}</pre>
        </div>
      ) : null}

      {status ? (
        <div className="lc-card">
          <div className="lc-section-title">Legal Bot Status</div>
          <pre className="lc-pre">{JSON.stringify(status, null, 2)}</pre>
        </div>
      ) : null}
    </div>
  );
}
