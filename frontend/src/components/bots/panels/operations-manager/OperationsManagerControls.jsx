import React, { useState } from "react";

const INITIAL_WORKFLOWS = [
    { id: 1, name: "Order Processing", type: "automated", priority: "high", tasks: 12, state: "idle" },
    { id: 2, name: "Inventory Management", type: "scheduled", priority: "medium", tasks: 8, state: "idle" },
    { id: 3, name: "Customer Support", type: "manual", priority: "high", tasks: 5, state: "paused" },
    { id: 4, name: "Reporting", type: "automated", priority: "low", tasks: 3, state: "running" },
];

const INITIAL_TASKS = [
    { id: 1, name: "Process new orders", workflow: "Order Processing", status: "pending", eta: "5m" },
    { id: 2, name: "Update inventory levels", workflow: "Inventory Management", status: "in-progress", eta: "10m" },
    { id: 3, name: "Generate daily report", workflow: "Reporting", status: "completed", eta: "2m" },
    { id: 4, name: "Optimize shipping routes", workflow: "Logistics", status: "pending", eta: "15m" },
];

export default function OperationsManagerControls({ activeTab }) {
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [workflows, setWorkflows] = useState(INITIAL_WORKFLOWS);
    const [tasks, setTasks] = useState(INITIAL_TASKS);
    const [taskSearch, setTaskSearch] = useState("");
    const [taskStatusFilter, setTaskStatusFilter] = useState("all");
    const [actionNotice, setActionNotice] = useState("");
    const [optimizationSettings, setOptimizationSettings] = useState({
        autoOptimize: true,
        balanceResources: true,
        predictiveScheduling: false,
    });

    const selectedWorkflowRecord = workflows.find((workflow) => workflow.id === selectedWorkflow) || null;

    const setWorkflowState = (nextState) => {
        if (!selectedWorkflowRecord) {
            setActionNotice("Select a workflow before running an action.");
            return;
        }

        setWorkflows((current) =>
            current.map((workflow) =>
                workflow.id === selectedWorkflowRecord.id
                    ? { ...workflow, state: nextState }
                    : workflow
            )
        );
        setActionNotice(`${selectedWorkflowRecord.name} is now ${nextState}.`);
    };

    const handleOptimizeWorkflow = () => {
        if (!selectedWorkflowRecord) {
            setActionNotice("Select a workflow before optimization.");
            return;
        }

        setWorkflows((current) =>
            current.map((workflow) =>
                workflow.id === selectedWorkflowRecord.id
                    ? {
                        ...workflow,
                        state: "optimized",
                        priority: workflow.priority === "low" ? "medium" : workflow.priority,
                    }
                    : workflow
            )
        );
        setActionNotice(`${selectedWorkflowRecord.name} has been optimized.`);
    };

    const handleNewTask = () => {
        const workflowName = selectedWorkflowRecord?.name || "General Operations";
        const newTask = {
            id: Date.now(),
            name: `New task for ${workflowName}`,
            workflow: workflowName,
            status: "pending",
            eta: "20m",
        };
        setTasks((current) => [newTask, ...current]);
        setActionNotice(`Created a new task for ${workflowName}.`);
    };

    const handleExecuteTask = (taskId) => {
        let updatedTaskName = "Task";
        setTasks((current) =>
            current.map((task) => {
                if (task.id !== taskId) return task;

                updatedTaskName = task.name;
                if (task.status === "pending") return { ...task, status: "in-progress", eta: "8m" };
                if (task.status === "in-progress") return { ...task, status: "completed", eta: "done" };
                return { ...task, status: "pending", eta: "5m" };
            })
        );
        setActionNotice(`${updatedTaskName} status updated.`);
    };

    const handleOptimizationSettingChange = (field) => {
        setOptimizationSettings((current) => ({ ...current, [field]: !current[field] }));
    };

    const handleRunOptimization = () => {
        const enabledSettings = Object.entries(optimizationSettings)
            .filter(([, enabled]) => enabled)
            .map(([key]) => key.replace(/([A-Z])/g, " $1").toLowerCase());
        setActionNotice(
            enabledSettings.length
                ? `Optimization started with ${enabledSettings.join(", ")} enabled.`
                : "Optimization started with manual settings."
        );
    };

    const visibleTasks = tasks.filter((task) => {
        const matchesSearch =
            task.name.toLowerCase().includes(taskSearch.toLowerCase()) ||
            task.workflow.toLowerCase().includes(taskSearch.toLowerCase());
        const matchesStatus = taskStatusFilter === "all" || task.status === taskStatusFilter;
        return matchesSearch && matchesStatus;
    });

    const renderWorkflowsTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Workflow Management</div>
            {actionNotice ? <div className="ops-card-ghost">{actionNotice}</div> : null}
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
                                <span className="ops-muted">{workflow.state}</span>
                                <span className="ops-muted">{workflow.tasks} tasks</span>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="ops-column ops-actions">
                    <button type="button" className="ops-btn primary" onClick={() => setWorkflowState("running")}>Start Workflow</button>
                    <button type="button" className="ops-btn" onClick={() => setWorkflowState("paused")}>Pause</button>
                    <button type="button" className="ops-btn" onClick={handleOptimizeWorkflow}>Optimize</button>
                    <button type="button" className="ops-btn danger" onClick={() => setWorkflowState("stopped")}>Stop</button>
                </div>
            </div>
        </div>
    );

    const renderTasksTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Task Manager</div>
            {actionNotice ? <div className="ops-card-ghost">{actionNotice}</div> : null}
            <div className="ops-row ops-task-bar">
                <input
                    className="ops-input"
                    type="text"
                    placeholder="Search tasks..."
                    value={taskSearch}
                    onChange={(event) => setTaskSearch(event.target.value)}
                />
                <select className="ops-select" value={taskStatusFilter} onChange={(event) => setTaskStatusFilter(event.target.value)}>
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                </select>
                <button type="button" className="ops-btn" onClick={handleNewTask}>+ New Task</button>
            </div>
            <div className="ops-column">
                {visibleTasks.map((task) => (
                    <div key={task.id} className="ops-list-item">
                        <div className="ops-list-head">
                            <div className="ops-task-check" />
                            <span className="ops-list-name">{task.name}</span>
                            <span className="ops-muted">{task.workflow}</span>
                        </div>
                        <div className="ops-list-meta">
                            <span className={`ops-status-tag ${task.status}`}>{task.status}</span>
                            <span className="ops-muted">{task.eta}</span>
                            <button type="button" className="ops-btn ghost" onClick={() => handleExecuteTask(task.id)}>Execute</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderPerformanceTab = () => (
        <div className="ops-section">
            <div className="ops-card-title">Performance Optimization</div>
            {actionNotice ? <div className="ops-card-ghost">{actionNotice}</div> : null}
            <div className="ops-row">
                <div className="ops-column ops-card-ghost">
                    <div className="ops-section-sub">Workflow Optimization</div>
                    <label className="ops-toggle">
                        <input type="checkbox" checked={optimizationSettings.autoOptimize} onChange={() => handleOptimizationSettingChange("autoOptimize")} /> Auto-optimize workflows
                    </label>
                    <label className="ops-toggle">
                        <input type="checkbox" checked={optimizationSettings.balanceResources} onChange={() => handleOptimizationSettingChange("balanceResources")} /> Balance resource allocation
                    </label>
                    <label className="ops-toggle">
                        <input type="checkbox" checked={optimizationSettings.predictiveScheduling} onChange={() => handleOptimizationSettingChange("predictiveScheduling")} /> Predictive scheduling
                    </label>
                    <button type="button" className="ops-btn primary" onClick={handleRunOptimization}>Run Optimization</button>
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
