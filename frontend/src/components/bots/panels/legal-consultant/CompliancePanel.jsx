import { useState } from "react";

export default function CompliancePanel({ service, disabled }) {
  const [jurisdiction, setJurisdiction] = useState("usa");
  const [activity, setActivity] = useState("");
  const [result, setResult] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [regulations, setRegulations] = useState(null);

  const check = async () => {
    const res = await service.checkCompliance({ activity, jurisdiction });
    setResult(res);
  };

  const status = async () => {
    const res = await service.complianceStatus({ jurisdiction });
    setResult(res);
  };

  const loadAlerts = async () => {
    const res = await service.complianceAlerts({ jurisdiction });
    setAlerts(res);
  };

  const loadRegs = async () => {
    const res = await service.regulations({ jurisdiction });
    setRegulations(res);
  };

  return (
    <div className="lc-col">
      <div className="lc-card">
        <div className="lc-section-title">Compliance Tools</div>
        <div className="lc-grid">
          <div className="lc-field">
            <label>Jurisdiction</label>
            <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
              <option value="usa">USA</option>
              <option value="canada">Canada</option>
              <option value="uae">UAE</option>
              <option value="gcc">GCC</option>
              <option value="international">International</option>
            </select>
          </div>
          <div className="lc-field">
            <label>Activity</label>
            <input value={activity} onChange={(e) => setActivity(e.target.value)} placeholder="e.g. freight contract" />
          </div>
        </div>
        <div className="lc-actions">
          <button onClick={check} disabled={disabled}>Check Activity</button>
          <button onClick={status} disabled={disabled}>Status Report</button>
          <button onClick={loadAlerts} disabled={disabled}>Load Alerts</button>
          <button onClick={loadRegs} disabled={disabled}>Load Regulations</button>
        </div>
      </div>

      {result ? (
        <div className="lc-card">
          <div className="lc-section-title">Result</div>
          <pre className="lc-pre">{JSON.stringify(result, null, 2)}</pre>
        </div>
      ) : null}

      {alerts ? (
        <div className="lc-card">
          <div className="lc-section-title">Alerts</div>
          <pre className="lc-pre">{JSON.stringify(alerts, null, 2)}</pre>
        </div>
      ) : null}

      {regulations ? (
        <div className="lc-card">
          <div className="lc-section-title">Regulations</div>
          <pre className="lc-pre">{JSON.stringify(regulations, null, 2)}</pre>
        </div>
      ) : null}
    </div>
  );
}
