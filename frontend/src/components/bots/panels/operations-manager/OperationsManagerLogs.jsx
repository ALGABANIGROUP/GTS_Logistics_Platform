import React from "react";

export default function OperationsManagerLogs() {
    const logs = [
        { id: 1, level: "info", message: "Workflow order-processing started", time: "09:12" },
        { id: 2, level: "success", message: "Inventory sync completed", time: "09:25" },
        { id: 3, level: "warning", message: "Performance dip detected in shipping", time: "10:05" },
        { id: 4, level: "info", message: "Report generation finished", time: "10:20" },
    ];

    return (
        <div className="ops-section">
            <div className="ops-card-title">Activity & Logs</div>
            <div className="ops-column">
                {logs.map((log) => (
                    <div key={log.id} className={`ops-list-item ops-log ${log.level}`}>
                        <div className="ops-list-head">
                            <span className="ops-log-level">{log.level}</span>
                            <span className="ops-muted">{log.time}</span>
                        </div>
                        <div className="ops-list-meta">
                            <span>{log.message}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
