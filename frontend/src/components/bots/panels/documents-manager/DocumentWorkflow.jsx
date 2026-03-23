// src/components/bots/panels/documents-manager/DocumentWorkflow.jsx
import React, { useState, useEffect } from 'react';
import './DocumentWorkflow.css';

const DocumentWorkflow = () => {
    const [workflows, setWorkflows] = useState([]);
    const [activeWorkflow, setActiveWorkflow] = useState(null);
    const [newWorkflow, setNewWorkflow] = useState(null);

    const workflowTemplates = [
        {
            id: 'standard_import',
            name: 'Standard Import Workflow',
            description: 'Process imported shipment documents',
            steps: [
                { id: 1, name: 'Document Upload', icon: '', description: 'Upload shipping documents' },
                { id: 2, name: 'Classification', icon: '', description: 'Classify document type' },
                { id: 3, name: 'Data Extraction', icon: '', description: 'Extract key data via OCR' },
                { id: 4, name: 'Validation', icon: '', description: 'Validate against requirements' },
                { id: 5, name: 'Customs Filing', icon: '', description: 'Submit to customs' },
                { id: 6, name: 'Approval', icon: '', description: 'Wait for approval' },
                { id: 7, name: 'Archive', icon: '', description: 'Archive processed document' }
            ]
        },
        {
            id: 'export_procedure',
            name: 'Export Procedure Workflow',
            description: 'Process export shipment documents',
            steps: [
                { id: 1, name: 'Document Preparation', icon: '', description: 'Prepare export documents' },
                { id: 2, name: 'Quality Check', icon: '', description: 'Quality control verification' },
                { id: 3, name: 'Signature Collection', icon: '', description: 'Collect required signatures' },
                { id: 4, name: 'Electronic Filing', icon: '', description: 'File electronically' },
                { id: 5, name: 'Tracking', icon: '', description: 'Track shipment status' }
            ]
        },
        {
            id: 'customs_clearance',
            name: 'Customs Clearance Workflow',
            description: 'Handle customs clearance process',
            steps: [
                { id: 1, name: 'Documentation Review', icon: '', description: 'Review all documents' },
                { id: 2, name: 'Compliance Check', icon: '', description: 'Check compliance' },
                { id: 3, name: 'Duties Calculation', icon: '', description: 'Calculate duties and taxes' },
                { id: 4, name: 'Payment Processing', icon: '', description: 'Process payment' },
                { id: 5, name: 'Clearance Release', icon: '', description: 'Release for clearance' }
            ]
        }
    ];

    const [activeWorkflows, setActiveWorkflows] = useState([
        {
            id: 'wf-001',
            templateId: 'standard_import',
            name: 'Import - Order #12345',
            status: 'in_progress',
            currentStep: 3,
            createdAt: new Date(Date.now() - 86400000).toISOString(),
            documents: ['BOL-789456.pdf', 'Invoice-ABC-123.pdf'],
            progress: 45
        },
        {
            id: 'wf-002',
            templateId: 'export_procedure',
            name: 'Export - Shipment #67890',
            status: 'completed',
            currentStep: 5,
            createdAt: new Date(Date.now() - 172800000).toISOString(),
            documents: ['Packing-List-789.pdf'],
            progress: 100
        }
    ]);

    const getWorkflowTemplate = (templateId) => {
        return workflowTemplates.find(t => t.id === templateId);
    };

    const createWorkflow = (templateId) => {
        const template = getWorkflowTemplate(templateId);
        if (!template) return;

        const workflow = {
            id: `wf-${Date.now()}`,
            templateId,
            name: `${template.name} - ${new Date().toLocaleDateString()}`,
            status: 'pending',
            currentStep: 0,
            createdAt: new Date().toISOString(),
            documents: [],
            progress: 0
        };

        setActiveWorkflows([...activeWorkflows, workflow]);
        setNewWorkflow(null);
    };

    const startWorkflow = (workflowId) => {
        setActiveWorkflows(prev =>
            prev.map(wf =>
                wf.id === workflowId
                    ? { ...wf, status: 'in_progress', currentStep: 1, progress: 10 }
                    : wf
            )
        );
    };

    const completeStep = (workflowId) => {
        setActiveWorkflows(prev =>
            prev.map(wf => {
                if (wf.id !== workflowId) return wf;

                const template = getWorkflowTemplate(wf.templateId);
                const totalSteps = template?.steps.length || 1;
                const nextStep = Math.min(wf.currentStep + 1, totalSteps);
                const newProgress = Math.round((nextStep / totalSteps) * 100);
                const newStatus = nextStep === totalSteps ? 'completed' : 'in_progress';

                return {
                    ...wf,
                    currentStep: nextStep,
                    progress: newProgress,
                    status: newStatus
                };
            })
        );
    };

    const cancelWorkflow = (workflowId) => {
        setActiveWorkflows(prev =>
            prev.map(wf =>
                wf.id === workflowId ? { ...wf, status: 'cancelled' } : wf
            )
        );
    };

    return (
        <div className="document-workflow">
            <div className="workflow-header">
                <h2>Document Workflow Automation</h2>
                <p>Automate and track document processing workflows</p>
            </div>

            <div className="workflow-section">
                <div className="section-title">
                    <h3>Workflow Templates</h3>
                    <p>Start a new workflow from a template</p>
                </div>

                <div className="templates-grid">
                    {workflowTemplates.map(template => (
                        <div key={template.id} className="template-card">
                            <div className="template-header">
                                <h4>{template.name}</h4>
                                <span className="step-count">{template.steps.length} steps</span>
                            </div>
                            <p className="template-description">{template.description}</p>
                            <div className="template-steps-preview">
                                {template.steps.slice(0, 3).map(step => (
                                    <span key={step.id} className="step-preview">
                                        {step.icon} {step.name}
                                    </span>
                                ))}
                                {template.steps.length > 3 && (
                                    <span className="step-more">+{template.steps.length - 3} more</span>
                                )}
                            </div>
                            <button
                                className="template-btn"
                                onClick={() => createWorkflow(template.id)}
                            >
                                 Start Workflow
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="workflow-section">
                <div className="section-title">
                    <h3>Active Workflows</h3>
                    <p>Monitor and manage running workflows</p>
                </div>

                {activeWorkflows.length === 0 ? (
                    <div className="empty-workflows">
                        <div className="empty-icon"></div>
                        <p>No active workflows. Start one from a template above.</p>
                    </div>
                ) : (
                    <div className="workflows-list">
                        {activeWorkflows.map(workflow => {
                            const template = getWorkflowTemplate(workflow.templateId);
                            const currentStepData = template?.steps[workflow.currentStep - 1];

                            return (
                                <div
                                    key={workflow.id}
                                    className={`workflow-card ${workflow.status}`}
                                    onClick={() => setActiveWorkflow(workflow.id === activeWorkflow ? null : workflow.id)}
                                >
                                    <div className="workflow-card-header">
                                        <div className="workflow-info">
                                            <h4>{workflow.name}</h4>
                                            <div className="workflow-meta">
                                                <span className="workflow-id">{workflow.id}</span>
                                                <span className={`status-badge ${workflow.status}`}>
                                                    {workflow.status === 'in_progress' && ' In Progress'}
                                                    {workflow.status === 'completed' && ' Completed'}
                                                    {workflow.status === 'pending' && ' Pending'}
                                                    {workflow.status === 'cancelled' && ' Cancelled'}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="workflow-progress">
                                            <div className="progress-circle">
                                                <div className="progress-value">{workflow.progress}%</div>
                                            </div>
                                        </div>
                                    </div>

                                    {activeWorkflow === workflow.id && (
                                        <div className="workflow-details">
                                            <div className="details-section">
                                                <h5>Current Step: {currentStepData?.name}</h5>
                                                <p>{currentStepData?.description}</p>
                                            </div>

                                            <div className="details-section">
                                                <h5>Workflow Steps</h5>
                                                <div className="steps-timeline">
                                                    {template?.steps.map((step, index) => (
                                                        <div
                                                            key={step.id}
                                                            className={`timeline-step ${index < workflow.currentStep ? 'completed' : index === workflow.currentStep - 1 ? 'active' : 'pending'
                                                                }`}
                                                        >
                                                            <div className="step-marker">{step.icon}</div>
                                                            <div className="step-label">{step.name}</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="details-section">
                                                <h5>Associated Documents</h5>
                                                {workflow.documents.length === 0 ? (
                                                    <p className="empty-docs">No documents attached</p>
                                                ) : (
                                                    <ul className="docs-list">
                                                        {workflow.documents.map((doc, idx) => (
                                                            <li key={idx}> {doc}</li>
                                                        ))}
                                                    </ul>
                                                )}
                                            </div>

                                            <div className="workflow-actions">
                                                {workflow.status === 'pending' && (
                                                    <button
                                                        className="action-btn primary"
                                                        onClick={() => startWorkflow(workflow.id)}
                                                    >
                                                         Start Workflow
                                                    </button>
                                                )}
                                                {workflow.status === 'in_progress' && (
                                                    <>
                                                        <button
                                                            className="action-btn primary"
                                                            onClick={() => completeStep(workflow.id)}
                                                        >
                                                             Complete Current Step
                                                        </button>
                                                        <button
                                                            className="action-btn secondary"
                                                            onClick={() => cancelWorkflow(workflow.id)}
                                                        >
                                                             Cancel Workflow
                                                        </button>
                                                    </>
                                                )}
                                                {workflow.status === 'completed' && (
                                                    <button
                                                        className="action-btn secondary"
                                                        onClick={() => {
                                                            const newWf = {
                                                                ...workflow,
                                                                id: `wf-${Date.now()}`,
                                                                status: 'pending',
                                                                currentStep: 0,
                                                                progress: 0
                                                            };
                                                            setActiveWorkflows([...activeWorkflows, newWf]);
                                                        }}
                                                    >
                                                         Create Similar Workflow
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    <div className="workflow-progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{ width: `${workflow.progress}%` }}
                                        ></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <div className="workflow-statistics">
                <h3>Workflow Statistics</h3>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">{activeWorkflows.length}</div>
                        <div className="stat-label">Total Workflows</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">{activeWorkflows.filter(w => w.status === 'in_progress').length}</div>
                        <div className="stat-label">In Progress</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">{activeWorkflows.filter(w => w.status === 'completed').length}</div>
                        <div className="stat-label">Completed</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">
                            {Math.round(
                                activeWorkflows.reduce((sum, w) => sum + w.progress, 0) / activeWorkflows.length || 0
                            )}%
                        </div>
                        <div className="stat-label">Average Progress</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DocumentWorkflow;
