// src/components/bots/panels/documents-manager/AdvancedWorkflows.jsx
import React, { useState } from 'react';
import './AdvancedWorkflows.css';

const AdvancedWorkflows = () => {
    const [workflowMode, setWorkflowMode] = useState('designer'); // designer, templates, active
    const [workflowNotice, setWorkflowNotice] = useState('');
    const [customWorkflows, setCustomWorkflows] = useState([
        { id: 1, name: 'Express Import Clearance', steps: 8, triggers: 2, conditions: 5, actions: 3, created: '2024-01-10' },
        { id: 2, name: 'Export Document Pipeline', steps: 6, triggers: 1, conditions: 3, actions: 2, created: '2024-01-05' }
    ]);
    const [activeWorkflows, setActiveWorkflows] = useState([
        {
            id: 1,
            name: 'Standard Import',
            status: 'running',
            progress: 65,
            documentsProcessed: 245,
            averageTime: '2.3h',
            lastRun: '2024-01-15'
        },
        {
            id: 2,
            name: 'Customs Fast Track',
            status: 'running',
            progress: 42,
            documentsProcessed: 89,
            averageTime: '1.5h',
            lastRun: '2024-01-15'
        }
    ]);

    const workflowTemplates = [
        {
            id: 'standard_import',
            name: 'Standard Import Process',
            steps: ['Document Upload', 'OCR Processing', 'Data Extraction', 'Validation', 'Compliance Check', 'Approval'],
            triggers: ['Manual', 'Scheduled', 'Document Event'],
            description: 'Complete workflow for import document processing'
        },
        {
            id: 'express_export',
            name: 'Express Export',
            steps: ['Quick Upload', 'Instant OCR', 'Auto-Approve', 'Generate Certificate'],
            triggers: ['Manual', 'Document Event'],
            description: 'Fast-track export document processing'
        }
    ];

    const workflowComponents = [
        { id: 'trigger', name: 'Trigger', icon: '', description: 'Start workflow' },
        { id: 'condition', name: 'Condition', icon: '', description: 'If/else logic' },
        { id: 'action', name: 'Action', icon: '', description: 'Execute task' },
        { id: 'delay', name: 'Delay', icon: '', description: 'Wait time' },
        { id: 'loop', name: 'Loop', icon: '', description: 'Repeat action' },
        { id: 'parallel', name: 'Parallel', icon: '', description: 'Concurrent tasks' }
    ];

    const saveDesigner = () => setWorkflowNotice('Workflow draft saved locally.');
    const testDesigner = () => setWorkflowNotice('Workflow test started with sample documents.');
    const activateDesigner = () => setWorkflowNotice('Workflow designer configuration marked ready for activation.');
    const pauseWorkflow = (workflowId) => {
        setActiveWorkflows((prev) =>
            prev.map((workflow) =>
                workflow.id === workflowId ? { ...workflow, status: 'paused' } : workflow
            )
        );
        setWorkflowNotice(`Workflow ${workflowId} paused.`);
    };
    const viewWorkflowDetails = (workflowId) => {
        const workflow = activeWorkflows.find((item) => item.id === workflowId);
        if (workflow) {
            setWorkflowNotice(`${workflow.name}: ${workflow.documentsProcessed} documents processed, ${workflow.progress}% complete.`);
        }
    };
    const viewWorkflowLogs = (workflowId) => {
        const workflow = activeWorkflows.find((item) => item.id === workflowId);
        setWorkflowNotice(`Logs opened for ${workflow?.name || `workflow ${workflowId}`}.`);
    };
    const editWorkflow = (workflow) => {
        setWorkflowMode('designer');
        setWorkflowNotice(`Editing ${workflow.name} in the workflow designer.`);
    };
    const activateCustomWorkflow = (workflow) => {
        setActiveWorkflows((prev) =>
            prev.some((item) => item.name === workflow.name)
                ? prev
                : [
                    {
                        id: Date.now(),
                        name: workflow.name,
                        status: 'running',
                        progress: 0,
                        documentsProcessed: 0,
                        averageTime: '0.0h',
                        lastRun: new Date().toISOString().split('T')[0]
                    },
                    ...prev,
                ]
        );
        setWorkflowNotice(`${workflow.name} activated.`);
    };
    const duplicateWorkflow = (workflow) => {
        const duplicate = {
            ...workflow,
            id: Date.now(),
            name: `${workflow.name} Copy`,
            created: new Date().toISOString().split('T')[0]
        };
        setCustomWorkflows((prev) => [duplicate, ...prev]);
        setWorkflowNotice(`${workflow.name} duplicated.`);
    };
    const deleteWorkflow = (workflowId) => {
        setCustomWorkflows((prev) => prev.filter((workflow) => workflow.id !== workflowId));
        setWorkflowNotice(`Workflow ${workflowId} deleted.`);
    };

    return (
        <div className="advanced-workflows">
            <div className="workflows-header">
                <h2> Advanced Workflow Automation</h2>
                <p>Design custom document processing workflows with drag-and-drop builder</p>
            </div>

            {/* Mode Tabs */}
            <div className="workflow-tabs">
                <button
                    className={`tab-btn ${workflowMode === 'designer' ? 'active' : ''}`}
                    onClick={() => setWorkflowMode('designer')}
                >
                     Workflow Designer
                </button>
                <button
                    className={`tab-btn ${workflowMode === 'templates' ? 'active' : ''}`}
                    onClick={() => setWorkflowMode('templates')}
                >
                     Templates
                </button>
                <button
                    className={`tab-btn ${workflowMode === 'active' ? 'active' : ''}`}
                    onClick={() => setWorkflowMode('active')}
                >
                     Active Workflows
                </button>
            </div>

            {/* Workflow Designer */}
            {workflowMode === 'designer' && (
                <div className="workflow-designer">
                    <div className="designer-container">
                        <div className="components-panel">
                            <h3> Workflow Components</h3>
                            <div className="components-list">
                                {workflowComponents.map(comp => (
                                    <div key={comp.id} className="component-item" draggable>
                                        <div className="component-icon">{comp.icon}</div>
                                        <div className="component-info">
                                            <div className="component-name">{comp.name}</div>
                                            <div className="component-desc">{comp.description}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="canvas-area">
                            <div className="canvas-header">
                                <span> Drag components here to build workflow</span>
                                <div className="canvas-controls">
                                    <button className="canvas-btn" onClick={saveDesigner}> Save</button>
                                    <button className="canvas-btn" onClick={testDesigner}> Test</button>
                                    <button className="canvas-btn" onClick={activateDesigner}> Activate</button>
                                </div>
                            </div>
                            <div className="drop-zone">
                                <div className="empty-state">
                                    <div className="empty-icon"></div>
                                    <p>Drag workflow components here to create your custom process</p>
                                </div>
                            </div>
                        </div>

                        <div className="properties-panel">
                            <h3> Properties</h3>
                            <div className="properties-list">
                                <div className="property">
                                    <label>Workflow Name</label>
                                    <input type="text" placeholder="Enter workflow name" />
                                </div>
                                <div className="property">
                                    <label>Trigger Event</label>
                                    <select>
                                        <option>Manual</option>
                                        <option>Scheduled</option>
                                        <option>Document Event</option>
                                    </select>
                                </div>
                                <div className="property">
                                    <label>Max Execution Time</label>
                                    <input type="text" placeholder="e.g., 30 minutes" />
                                </div>
                                <div className="property">
                                    <label>Retry on Failure</label>
                                    <select>
                                        <option>Enabled (3 attempts)</option>
                                        <option>Disabled</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Templates */}
            {workflowMode === 'templates' && (
                <div className="templates-section">
                    <h3> Workflow Templates</h3>
                    <div className="templates-grid">
                        {workflowTemplates.map(template => (
                            <div key={template.id} className="template-card">
                                <div className="template-header">{template.name}</div>
                                <div className="template-description">{template.description}</div>

                                <div className="template-section">
                                    <div className="section-label">Steps ({template.steps.length})</div>
                                    <div className="steps-list">
                                        {template.steps.map((step, idx) => (
                                            <div key={idx} className="step-item">
                                                <span className="step-number">{idx + 1}</span>
                                                <span className="step-name">{step}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="template-section">
                                    <div className="section-label">Available Triggers</div>
                                    <div className="triggers-list">
                                        {template.triggers.map((trigger, idx) => (
                                            <span key={idx} className="trigger-tag">{trigger}</span>
                                        ))}
                                    </div>
                                </div>

                                <div className="template-actions">
                                    <button className="action-btn primary"> Use Template</button>
                                    <button className="action-btn secondary"> Preview</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Active Workflows */}
            {workflowMode === 'active' && (
                <div className="active-workflows">
                    <h3> Currently Running Workflows</h3>
                    <div className="workflows-list">
                        {activeWorkflows.map(workflow => (
                            <div key={workflow.id} className="workflow-card">
                                <div className="workflow-top">
                                    <div className="workflow-title">{workflow.name}</div>
                                    <span className={`workflow-status ${workflow.status}`}>{workflow.status}</span>
                                </div>

                                <div className="progress-section">
                                    <div className="progress-label">Overall Progress: {workflow.progress}%</div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${workflow.progress}%` }}></div>
                                    </div>
                                </div>

                                <div className="workflow-stats">
                                    <div className="stat">
                                        <span className="stat-icon"></span>
                                        <div className="stat-text">
                                            <div className="stat-label">Documents</div>
                                            <div className="stat-value">{workflow.documentsProcessed}</div>
                                        </div>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-icon"></span>
                                        <div className="stat-text">
                                            <div className="stat-label">Avg Time</div>
                                            <div className="stat-value">{workflow.averageTime}</div>
                                        </div>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-icon"></span>
                                        <div className="stat-text">
                                            <div className="stat-label">Last Run</div>
                                            <div className="stat-value">{workflow.lastRun}</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="workflow-actions">
                                    <button className="action-btn pause" onClick={() => pauseWorkflow(workflow.id)}> Pause</button>
                                    <button className="action-btn view" onClick={() => viewWorkflowDetails(workflow.id)}> View Details</button>
                                    <button className="action-btn logs" onClick={() => viewWorkflowLogs(workflow.id)}> Logs</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Custom Workflows */}
            <div className="custom-workflows">
                <h3> Custom Workflows</h3>
                <div className="custom-workflows-grid">
                    {customWorkflows.map(wf => (
                        <div key={wf.id} className="custom-workflow-card">
                            <div className="card-header">{wf.name}</div>

                            <div className="workflow-details">
                                <div className="detail-row">
                                    <span className="detail-label">Steps:</span>
                                    <span className="detail-value">{wf.steps}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Triggers:</span>
                                    <span className="detail-value">{wf.triggers}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Conditions:</span>
                                    <span className="detail-value">{wf.conditions}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Actions:</span>
                                    <span className="detail-value">{wf.actions}</span>
                                </div>
                            </div>

                            <div className="workflow-meta">
                                <span className="created-date">Created: {wf.created}</span>
                            </div>

                            <div className="card-actions">
                                <button className="action-btn edit" onClick={() => editWorkflow(wf)}> Edit</button>
                                <button className="action-btn activate" onClick={() => activateCustomWorkflow(wf)}> Activate</button>
                                <button className="action-btn duplicate" onClick={() => duplicateWorkflow(wf)}> Duplicate</button>
                                <button className="action-btn delete" onClick={() => deleteWorkflow(wf.id)}> Delete</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {workflowNotice ? <div className="workflow-notice">{workflowNotice}</div> : null}

            {/* Workflow Statistics */}
            <div className="workflow-statistics">
                <h3> Workflow Statistics</h3>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-content">
                            <div className="stat-value">{customWorkflows.length}</div>
                            <div className="stat-label">Custom Workflows</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-content">
                            <div className="stat-value">{activeWorkflows.length}</div>
                            <div className="stat-label">Active Now</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-content">
                            <div className="stat-value">1,245</div>
                            <div className="stat-label">Completed This Month</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-content">
                            <div className="stat-value">98.5%</div>
                            <div className="stat-label">Success Rate</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdvancedWorkflows;
