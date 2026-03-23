import React from "react";

export default function OperationsManagerDashboard() {
    const workflows = [
        { id: 1, name: "Order Processing", status: "running", tasks: 12, completion: 75 },
        { id: 2, name: "Inventory Sync", status: "running", tasks: 8, completion: 90 },
        { id: 3, name: "Customer Onboarding", status: "paused", tasks: 5, completion: 40 },
        { id: 4, name: "Reporting", status: "completed", tasks: 15, completion: 100 },
    ];

    const performanceMetrics = [
        { metric: "Workflow Efficiency", value: 92, target: 90 },
        { metric: "Task Completion Rate", value: 98, target: 95 },
        { metric: "Resource Utilization", value: 85, target: 80 },
        { metric: "Error Rate", value: 1.2, target: 2 },
    ];

    const activities = [
        { icon: "", text: "Order #12345 processed successfully", time: "2 minutes ago" },
        { icon: "", text: "Inventory sync completed", time: "15 minutes ago" },
        { icon: "", text: "Workflow optimization needed for Shipping", time: "1 hour ago" },
    ];

    const botReports = [
        {
            bot: "AIGeneralManager",
            summary: "Executive weekly digest delivered (12 KPIs, 3 alerts).",
            status: "completed",
            time: "5m ago",
        },
        {
            bot: "AIOperationsManager",
            summary: "Workflow variance report: 2 queues above SLA, auto-balancing applied.",
            status: "in-progress",
            time: "12m ago",
        },
        {
            bot: "AIFinanceBot",
            summary: "AP/AR rollup ready; awaiting approval for 3 invoices >$10k.",
            status: "pending",
            time: "25m ago",
        },
        {
            bot: "AIFreightBroker",
            summary: "Market pulse: spot rates +3.1% on reefer lanes; 2 lanes flagged for review.",
            status: "completed",
            time: "40m ago",
        },
    ];

    return (
        <div className="ops-section">
            <div className="ops-section-header">
                <div>
                    <div className="ops-section-title">Operations Dashboard</div>
                    <div className="ops-section-sub">Today</div>
                </div>
                <select className="ops-select">
                    <option>Last 24 hours</option>
                    <option>Last 7 days</option>
                    <option>Last 30 days</option>
                </select>
            </div>

            <div className="ops-grid ops-grid-quick">
                <button className="ops-quick-btn"> Optimize Workflows</button>
                <button className="ops-quick-btn"> Schedule Tasks</button>
                <button className="ops-quick-btn"> Analyze Performance</button>
                <button className="ops-quick-btn"> Configure Alerts</button>
            </div>

            <div className="ops-card">
                <div className="ops-card-title">Active Workflows</div>
                <div className="ops-grid ops-grid-workflows">
                    {workflows.map((workflow) => (
                        <div key={workflow.id} className="ops-workflow-card">
                            <div className="ops-workflow-head">
                                <span className="ops-workflow-name">{workflow.name}</span>
                                <span className={`ops-status-badge ${workflow.status}`}>{workflow.status}</span>
                            </div>
                            <div className="ops-progress">
                                <div className="ops-progress-bar" style={{ width: `${workflow.completion}%` }}>
                                    <span>{workflow.completion}%</span>
                                </div>
                            </div>
                            <div className="ops-workflow-foot">
                                <span>Tasks: {workflow.tasks}</span>
                                <button className="ops-chip">Manage</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="ops-card">
                <div className="ops-card-title">Performance Metrics</div>
                <div className="ops-grid ops-grid-metrics">
                    {performanceMetrics.map((metric, index) => (
                        <div key={index} className="ops-metric-card">
                            <div className="ops-metric-head">
                                <span className="ops-metric-name">{metric.metric}</span>
                                <span className={`ops-metric-value ${metric.value >= metric.target ? "ok" : "warn"}`}>
                                    {metric.value}
                                    {metric.metric.includes("Rate") ? "%" : ""}
                                </span>
                            </div>
                            <div className="ops-metric-target">
                                Target: {metric.target}
                                {metric.metric.includes("Rate") ? "%" : ""}
                            </div>
                            <div className="ops-progress-lite">
                                <div
                                    className="ops-progress-lite-bar"
                                    style={{ width: `${Math.min((metric.value / metric.target) * 100, 120)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="ops-card">
                <div className="ops-card-title">Recent Activities</div>
                <div className="ops-activities">
                    {activities.map((activity, idx) => (
                        <div key={idx} className="ops-activity-item">
                            <span className="ops-activity-icon">{activity.icon}</span>
                            <div className="ops-activity-text">
                                <span className="ops-activity-main">{activity.text}</span>
                                <span className="ops-activity-time">{activity.time}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="ops-card">
                <div className="ops-card-title">Bot Reports Received</div>
                <div className="ops-column">
                    {botReports.map((report, idx) => (
                        <div key={idx} className="ops-list-item">
                            <div className="ops-list-head">
                                <span className="ops-list-name">{report.bot}</span>
                                <span className={`ops-status-tag ${report.status}`}>{report.status}</span>
                                <span className="ops-muted">{report.time}</span>
                            </div>
                            <div className="ops-list-meta">
                                <span className="ops-muted">{report.summary}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
