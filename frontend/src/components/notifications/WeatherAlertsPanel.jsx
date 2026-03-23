// WeatherAlertsPanel.jsx - Display sent weather alerts
import React from 'react';
import { AlertTriangle, CheckCircle, Clock, User } from 'lucide-react';

const WeatherAlertsPanel = ({ alerts }) => {
    if (!alerts || alerts.length === 0) {
        return null;
    }

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical':
                return <AlertTriangle className="h-5 w-5 text-red-400" />;
            case 'high':
                return <AlertTriangle className="h-5 w-5 text-orange-400" />;
            case 'medium':
                return <AlertTriangle className="h-5 w-5 text-amber-400" />;
            default:
                return <AlertTriangle className="h-5 w-5 text-blue-400" />;
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical':
                return 'border-red-500/50 bg-red-900/20';
            case 'high':
                return 'border-orange-500/50 bg-orange-900/20';
            case 'medium':
                return 'border-amber-500/50 bg-amber-900/20';
            default:
                return 'border-blue-500/50 bg-blue-900/20';
        }
    };

    return (
        <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-4 backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-400" />
                    <h3 className="text-lg font-semibold text-white">Weather Alerts Sent</h3>
                    <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-xs font-semibold text-amber-300">
                        {alerts.length} Active
                    </span>
                </div>
            </div>

            <div className="space-y-2">
                {alerts.map((alert, index) => (
                    <div
                        key={index}
                        className={`rounded-lg border p-3 ${getSeverityColor(alert.severity)}`}
                    >
                        <div className="flex items-start gap-3">
                            {getSeverityIcon(alert.severity)}
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <span className="font-semibold text-white">{alert.title}</span>
                                    {alert.delivered && (
                                        <CheckCircle className="h-4 w-4 text-green-400" />
                                    )}
                                </div>
                                <p className="mt-1 text-sm text-slate-300">{alert.message}</p>
                                <div className="mt-2 flex items-center gap-4 text-xs text-slate-400">
                                    <div className="flex items-center gap-1">
                                        <User className="h-3 w-3" />
                                        <span>Driver ID: {alert.recipient_id}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <Clock className="h-3 w-3" />
                                        <span>{new Date(alert.sent_at).toLocaleTimeString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default WeatherAlertsPanel;
