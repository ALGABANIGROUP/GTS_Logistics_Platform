import React, { useState } from "react";

export default function OperationsManagerControls({ activeTab }) {
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);

    const workflows = [
        { id: 1, name: "Order Processing", type: "automated", priority: "high", tasks: 12 },
        { id: 2, name: "Inventory Management", type: "scheduled", priority: "medium", tasks: 8 },
        { id: 3, name: "Customer Support", type: "manual", priority: "high", tasks: 5 },
        { id: 4, name: "Reporting", type: "automated", priority: "low", tasks: 3 },
    ];

    const tasks = [
        { id: 1, name: "Process new orders", workflow: "Order Processing", status: "pending", eta: "5m" },
        { id: 2, name: "Update inventory levels", workflow: "Inventory Management", status: "in-progress", eta: "10m" },
        { id: 3, name: "Generate daily report", workflow: "Reporting", status: "completed", eta: "2m" },
        { id: 4, name: "Optimize shipping routes", workflow: "Logistics", status: "pending", eta: "15m" },
    ];

    const renderWorkflowsTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Workflow Management</div>
            <div className="ops-row">
                <div className="ops-column">
                    {workflows.map((workflow) => (
                        <div
                            key={workflow.id}
                            className={`ops-list-item ${selectedWorkflow === workflow.id ? "selected" : ""}`}
                            onClick={() => setSelectedWorkflow(workflow.id)}
                        >
                            <div className="ops-list-head">
                                <span className="ops-list-name">{workflow.name}</span>
                                <span className={`ops-chip ${workflow.type}`}>{workflow.type}</span>
                            </div>
                            <div className="ops-list-meta">
                                <span className={`ops-priority ${workflow.priority}`}>{workflow.priority}</span>
                                <span className="ops-muted">{workflow.tasks} tasks</span>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="ops-column ops-actions">
                    <button className="ops-btn primary">Start Workflow</button>
                    <button className="ops-btn">Pause</button>
                    <button className="ops-btn">Optimize</button>
                    <button className="ops-btn danger">Stop</button>
                </div>
            </div>
        </div>
    );

    const renderTasksTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Task Manager</div>
            <div className="ops-row ops-task-bar">
                <input className="ops-input" type="text" placeholder="Search tasks..." />
                <select className="ops-select">
                    <option>All Status</option>
                    <option>Pending</option>
                    <option>In Progress</option>
                    <option>Completed</option>
                </select>
                <button className="ops-btn">+ New Task</button>
            </div>
            <div className="ops-column">
                {tasks.map((task) => (
                    <div key={task.id} className="ops-list-item">
                        <div className="ops-list-head">
                            <div className="ops-task-check" />
                            <span className="ops-list-name">{task.name}</span>
                            <span className="ops-muted">{task.workflow}</span>
                        </div>
                        <div className="ops-list-meta">
                            <span className={`ops-status-tag ${task.status}`}>{task.status}</span>
                            <span className="ops-muted">{task.eta}</span>
                            <button className="ops-btn ghost">Execute</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderPerformanceTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Performance Optimization</div>
            <div className="ops-row">
                <div className="ops-column ops-card-ghost">
                    <div className="ops-section-sub">Workflow Optimization</div>
                    <label className="ops-toggle">
                        <input type="checkbox" defaultChecked /> Auto-optimize workflows
                    </label>
                    <label className="ops-toggle">
                        <input type="checkbox" defaultChecked /> Balance resource allocation
                    </label>
                    <label className="ops-toggle">
                        <input type="checkbox" /> Predictive scheduling
                    </label>
                    <button className="ops-btn primary">Run Optimization</button>
                </div>
                <div className="ops-column ops-card-ghost">
                    <div className="ops-section-sub">Performance Analytics</div>
                    <div className="ops-metric-row">
                        <span>Bottlenecks Detected</span>
                        <span className="ops-metric-number">3</span>
                    </div>
                    <div className="ops-metric-row">
                        <span>Optimization Potential</span>
                        <span className="ops-metric-number">23%</span>
                    </div>
                    <div className="ops-metric-row">
                        <span>Avg Efficiency Gain</span>
                        <span className="ops-metric-number">15%</span>
                    </div>
                </div>
            </div>
        </div>
    );

    switch (activeTab) {
        case "workflows":
            return renderWorkflowsTab();
        case "tasks":
            return renderTasksTab();
        case "performance":
            return renderPerformanceTab();
        default:
            return renderWorkflowsTab();
    }
}
