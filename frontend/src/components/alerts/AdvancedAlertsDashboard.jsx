// frontend/src/components/alerts/AdvancedAlertsDashboard.jsx
import React, { useState, useEffect } from 'react';

const AdvancedAlertsDashboard = () => {
    const [alerts, setAlerts] = useState([]);
    const [alertRules, setAlertRules] = useState([]);
    const [newRule, setNewRule] = useState({});

    useEffect(() => {
        loadAlerts();
        loadAlertRules();
    }, []);

    const loadAlerts = async () => {
        const recentAlerts = await window.alertSystem.getRecentAlerts();
        setAlerts(recentAlerts);
    };

    const loadAlertRules = async () => {
        const rules = await window.alertSystem.getAlertRules();
        setAlertRules(rules);
    };

    const acknowledgeAlert = async (alertId) => {
        await window.alertSystem.acknowledgeAlert(alertId);
        loadAlerts();
    };

    const addNewRule = () => {
        window.alertSystem.addAlertRule(newRule);
        setNewRule({});
        loadAlertRules();
    };

    return (
        <div className="p-6 space-y-6">
            <h2 className="text-2xl font-bold">🔔 Advanced Alerts System</h2>

            <div className="grid grid-cols-3 gap-6">

                {/* Active Alerts */}
                <div className="col-span-2 space-y-4">
                    <h3 className="text-xl font-semibold">🚨 Active Alerts</h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {alerts.map(alert => (
                            <div
                                key={alert.id}
                                className={`p-4 rounded-lg border-l-4 ${alert.severity === 'high'
                                        ? 'border-red-500 bg-red-50'
                                        : alert.severity === 'medium'
                                            ? 'border-orange-500 bg-orange-50'
                                            : 'border-yellow-500 bg-yellow-50'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <div className="font-medium">{alert.message}</div>
                                        <div className="text-sm text-gray-600 mt-1">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </div>
                                    </div>

                                    {!alert.acknowledged && (
                                        <button
                                            onClick={() => acknowledgeAlert(alert.id)}
                                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
                                        >
                                            Acknowledge
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Alert Rules Management */}
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold">⚙️ Alert Rules</h3>

                    <div className="bg-white p-4 rounded-lg shadow space-y-3">
                        <input
                            type="text"
                            placeholder="Rule Name"
                            value={newRule.name || ''}
                            onChange={(e) =>
                                setNewRule({ ...newRule, name: e.target.value })
                            }
                            className="w-full border rounded px-3 py-2"
                        />

                        <select
                            value={newRule.condition || ''}
                            onChange={(e) =>
                                setNewRule({ ...newRule, condition: e.target.value })
                            }
                            className="w-full border rounded px-3 py-2"
                        >
                            <option value="">Choose Condition</option>
                            <option value="threshold">Threshold Exceeded</option>
                            <option value="anomaly">Anomaly Detection</option>
                            <option value="pattern">Pattern Match</option>
                        </select>

                        <button
                            onClick={addNewRule}
                            className="w-full bg-green-600 text-white py-2 rounded"
                        >
                            Add Rule
                        </button>
                    </div>

                    <div className="space-y-2">
                        {alertRules.map((rule) => (
                            <div
                                key={rule.id}
                                className="flex justify-between items-center p-3 bg-gray-50 rounded"
                            >
                                <span className="font-medium">{rule.name}</span>
                                <span
                                    className={`px-2 py-1 rounded text-xs ${rule.triggered
                                            ? 'bg-red-100 text-red-800'
                                            : 'bg-green-100 text-green-800'
                                        }`}
                                >
                                    {rule.triggered ? 'Active' : 'Idle'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AdvancedAlertsDashboard;
