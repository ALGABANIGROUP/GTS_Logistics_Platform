import React, { useState } from "react";

export default function FinanceConfig() {
    const [settings, setSettings] = useState({
        autoInvoicing: true,
        autoReconcile: true,
        alertsEnabled: true,
        currency: "USD",
    });

    const onToggle = (key) => setSettings((prev) => ({ ...prev, [key]: !prev[key] }));

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
                        <button className="fin-btn">Reset</button>
                        <button className="fin-btn primary">Save</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
