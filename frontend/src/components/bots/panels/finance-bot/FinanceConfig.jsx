import React, { useState } from "react";

const STORAGE_KEY = "finance_bot_config";

export default function FinanceConfig() {
    const defaultSettings = {
        autoInvoicing: true,
        autoReconcile: true,
        alertsEnabled: true,
        currency: "USD",
    };
    const [settings, setSettings] = useState(() => {
        try {
            const saved = window.localStorage.getItem(STORAGE_KEY);
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch {
            return defaultSettings;
        }
    });
    const [feedback, setFeedback] = useState("");

    const onToggle = (key) => setSettings((prev) => ({ ...prev, [key]: !prev[key] }));
    const handleReset = () => {
        setSettings(defaultSettings);
        window.localStorage.removeItem(STORAGE_KEY);
        setFeedback("Configuration reset to defaults.");
    };
    const handleSave = () => {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        setFeedback("Configuration saved locally.");
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">Configuration</div>
            <div className="fin-grid fin-grid-compact">
                <div className="fin-card">
                    <div className="fin-card-sub">Automation</div>
                    <label className="fin-toggle">
                        <input type="checkbox" checked={settings.autoInvoicing} onChange={() => onToggle("autoInvoicing")} />
                        <span>Auto generate invoices</span>
                    </label>
                    <label className="fin-toggle">
                        <input type="checkbox" checked={settings.autoReconcile} onChange={() => onToggle("autoReconcile")} />
                        <span>Auto reconcile payments</span>
                    </label>
                    <label className="fin-toggle">
                        <input type="checkbox" checked={settings.alertsEnabled} onChange={() => onToggle("alertsEnabled")} />
                        <span>Alerts and reminders</span>
                    </label>
                </div>
                <div className="fin-card">
                    <div className="fin-card-sub">Defaults</div>
                    <label className="fin-field">
                        <span>Currency</span>
                        <select className="fin-select" value={settings.currency} onChange={(e) => setSettings((prev) => ({ ...prev, currency: e.target.value }))}>
                            <option value="USD">USD</option>
                            <option value="CAD">CAD</option>
                            <option value="EUR">EUR</option>
                        </select>
                    </label>
                    <div className="fin-row fin-gap-sm fin-justify-end">
                        <button className="fin-btn" onClick={handleReset}>Reset</button>
                        <button className="fin-btn primary" onClick={handleSave}>Save</button>
                    </div>
                    {feedback ? <div className="fin-muted">{feedback}</div> : null}
                </div>
            </div>
        </div>
    );
}
