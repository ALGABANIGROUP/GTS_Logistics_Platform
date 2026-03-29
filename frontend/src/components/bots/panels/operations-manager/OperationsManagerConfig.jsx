import React, { useState } from "react";

const STORAGE_KEY = "operations_manager_config";

export default function OperationsManagerConfig() {
    const defaultSettings = {
        autoOptimization: true,
        maxConcurrentWorkflows: 10,
        alertThreshold: 80,
        performanceMonitoring: true,
        resourceAllocation: "balanced",
        backupFrequency: "daily",
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

    const handleSettingChange = (key, value) => {
        setSettings((prev) => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        setFeedback("Configuration saved locally.");
    };

    const handleReset = () => {
        setSettings(defaultSettings);
        window.localStorage.removeItem(STORAGE_KEY);
        setFeedback("Configuration reset to defaults.");
    };

    const handleExport = () => {
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = "operations-manager-config.json";
        anchor.click();
        URL.revokeObjectURL(url);
        setFeedback("Configuration exported.");
    };

    return (
        <div className="ops-section">
            <div className="ops-card-title">Configuration Settings</div>
            <div className="ops-grid ops-grid-config">
                <div className="ops-card-ghost">
                    <div className="ops-section-sub">General</div>
                    <label className="ops-toggle">
                        <input
                            type="checkbox"
                            checked={settings.autoOptimization}
                            onChange={(e) => handleSettingChange("autoOptimization", e.target.checked)}
                        />
                        Auto workflow optimization
                    </label>
                    <label className="ops-toggle">
                        <input
                            type="checkbox"
                            checked={settings.performanceMonitoring}
                            onChange={(e) => handleSettingChange("performanceMonitoring", e.target.checked)}
                        />
                        Performance monitoring
                    </label>
                </div>

                <div className="ops-card-ghost">
                    <div className="ops-section-sub">Resource Management</div>
                    <label className="ops-field">
                        <span>Max concurrent workflows</span>
                        <input
                            type="number"
                            min="1"
                            max="50"
                            value={settings.maxConcurrentWorkflows}
                            onChange={(e) => handleSettingChange("maxConcurrentWorkflows", parseInt(e.target.value, 10))}
                        />
                    </label>
                    <label className="ops-field">
                        <span>Resource allocation</span>
                        <select
                            value={settings.resourceAllocation}
                            onChange={(e) => handleSettingChange("resourceAllocation", e.target.value)}
                        >
                            <option value="balanced">Balanced</option>
                            <option value="performance">Performance</option>
                            <option value="efficient">Efficiency</option>
                        </select>
                    </label>
                </div>

                <div className="ops-card-ghost">
                    <div className="ops-section-sub">Alerts</div>
                    <label className="ops-field">
                        <span>Performance alert threshold (%)</span>
                        <input
                            type="range"
                            min="50"
                            max="100"
                            value={settings.alertThreshold}
                            onChange={(e) => handleSettingChange("alertThreshold", parseInt(e.target.value, 10))}
                        />
                        <span className="ops-muted">{settings.alertThreshold}%</span>
                    </label>
                </div>

                <div className="ops-card-ghost">
                    <div className="ops-section-sub">Backup & Recovery</div>
                    <label className="ops-field">
                        <span>Backup frequency</span>
                        <select
                            value={settings.backupFrequency}
                            onChange={(e) => handleSettingChange("backupFrequency", e.target.value)}
                        >
                            <option value="hourly">Hourly</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                        </select>
                    </label>
                </div>
            </div>

            <div className="ops-row ops-actions-bar">
                <div className="ops-muted">{feedback || "Changes are stored locally until API sync is enabled."}</div>
                <div className="ops-actions">
                    <button className="ops-btn primary" onClick={handleSave}>Save</button>
                    <button className="ops-btn ghost" onClick={handleReset}>Reset</button>
                    <button className="ops-btn ghost" onClick={handleExport}>Export</button>
                </div>
            </div>
        </div>
    );
}
