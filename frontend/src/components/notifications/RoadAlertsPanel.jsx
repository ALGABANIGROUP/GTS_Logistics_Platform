// RoadAlertsPanel.jsx - Display road conditions and alerts
import React from 'react';
import { AlertTriangle, AlertCircle, Zap, CheckCircle2, Clock } from 'lucide-react';

const RoadAlertsPanel = ({ roadAlerts = [], combinedAlerts = [] }) => {
    const allAlerts = [...combinedAlerts, ...roadAlerts];

    if (allAlerts.length === 0) {
        return null;
    }

    const getSeverityColor = (type) => {
        if (type === 'combined') {
            return 'border-red-600 bg-red-900/20';
        }

        return 'border-orange-600 bg-orange-900/20';
    };

    const getSeverityIcon = (type) => {
        if (type === 'combined') {
            return <Zap className="h-4 w-4 text-yellow-400" />;
        }

        return <AlertCircle className="h-4 w-4 text-orange-500" />;
    };

    const getSeverityBadgeColor = (type) => {
        if (type === 'combined') {
            return 'bg-red-600 text-white';
        }

        return 'bg-orange-600 text-white';
    };

    return (
        <div className="mt-6 rounded-lg border border-slate-700 bg-slate-900/50 p-4">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-200">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                Road Condition Alerts
                <span className="ml-auto rounded-full bg-orange-600/30 px-2 py-0.5 text-xs font-normal text-orange-300">
                    {allAlerts.length} Alert(s)
                </span>
            </h3>

            <div className="space-y-3">
                {allAlerts.map((alert, idx) => (
                    <div
                        key={`${alert.type}-${idx}`}
                        className={`flex items-start gap-3 rounded-md border p-3 text-sm ${getSeverityColor(alert.type)}`}
                    >
                        <div className="mt-0.5">
                            {getSeverityIcon(alert.type)}
                        </div>

                        <div className="flex-1">
                            <div className="flex items-start justify-between gap-2">
                                <div>
                                    <p className="font-medium text-slate-100">
                                        {alert.title}
                                    </p>
                                    {alert.sources && alert.sources.length > 0 && (
                                        <p className="mt-1 text-xs text-slate-400">
                                            Sources: {alert.sources.join(' + ')}
                                        </p>
                                    )}
                                </div>
                                <span className={`whitespace-nowrap rounded px-2 py-1 text-xs font-semibold ${getSeverityBadgeColor(alert.type)}`}>
                                    {alert.type === 'combined' ? '🚨 Critical' : '⚠️ Warning'}
                                </span>
                            </div>

                            <div className="mt-2 space-y-1 text-xs text-slate-300">
                                {alert.sources && alert.sources.includes('road') && (
                                    <>
                                        <p>🛣️ Road: {alert.title}</p>
                                    </>
                                )}
                                {alert.sources && alert.sources.includes('weather') && (
                                    <>
                                        <p>🌡️ Weather: {alert.sources && alert.sources.includes('weather') ? 'Poor' : ''}</p>
                                    </>
                                )}
                            </div>

                            <div className="mt-2 flex items-center justify-between gap-2">
                                <div className="flex items-center gap-1 text-xs text-slate-400">
                                    <Clock className="h-3 w-3" />
                                    {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString('en-US') : 'Now'}
                                </div>

                                <div className="flex items-center gap-1">
                                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                                    <span className="text-xs text-green-400">Sent to Driver #{alert.driverId}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RoadAlertsPanel;
