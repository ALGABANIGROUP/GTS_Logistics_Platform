// src/components/bots/panels/documents-manager/ComplianceChecker.jsx
import React, { useState, useEffect } from 'react';
import './ComplianceChecker.css';
import documentsService from '../../../../services/documentsService';

const ComplianceChecker = () => {
    const [complianceChecks, setComplianceChecks] = useState([]);
    const [selectedDocuments, setSelectedDocuments] = useState([]);
    const [checkStatus, setCheckStatus] = useState('idle'); // idle, checking, completed
    const [complianceResults, setComplianceResults] = useState([]);

    const complianceRules = [
        { id: 'signature', name: 'Authorized Signature', required: true, icon: '' },
        { id: 'date', name: 'Valid Date', required: true, icon: '' },
        { id: 'amount', name: 'Amount Specified', required: true, icon: '' },
        { id: 'shipper', name: 'Shipper Details', required: true, icon: '' },
        { id: 'consignee', name: 'Consignee Details', required: true, icon: '' },
        { id: 'incoterms', name: 'Incoterms Specified', required: false, icon: '' },
        { id: 'hs_code', name: 'HS Code Present', required: false, icon: '' },
        { id: 'insurance', name: 'Insurance Details', required: false, icon: '' }
    ];

    const [availableDocuments, setAvailableDocuments] = useState([]);

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        try {
            const docs = await documentsService.listDocuments();
            setAvailableDocuments(docs);
            // Seed default selection: first two docs if available
            const seed = docs.slice(0, 2).map(d => d.id);
            if (seed.length) {
                setSelectedDocuments(seed);
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
        }
    };

    const runComplianceCheck = async () => {
        if (selectedDocuments.length === 0) return;

        setCheckStatus('checking');

        try {
            const results = await documentsService.runCompliance(selectedDocuments);
            setComplianceResults(results);
            setCheckStatus('completed');
        } catch (error) {
            console.error('Compliance check failed:', error);
            setComplianceResults([]);
            setCheckStatus('completed');
        }
    };

    const generateComplianceReport = () => {
        const report = {
            generated: new Date().toISOString(),
            totalChecked: complianceResults.length,
            compliant: complianceResults.filter(r => r.overallStatus === 'compliant').length,
            nonCompliant: complianceResults.filter(r => r.overallStatus === 'non-compliant').length,
            averageScore: Math.round(
                complianceResults.reduce((sum, r) => sum + r.complianceScore, 0) / complianceResults.length
            ),
            details: complianceResults
        };

        const csv = generateCSV(report);
        downloadReport(csv, `compliance-report-${Date.now()}.csv`);
    };

    const generateCSV = (report) => {
        let csv = 'Compliance Audit Report\n';
        csv += `Generated: ${report.generated}\n`;
        csv += `Total Checked: ${report.totalChecked}\n`;
        csv += `Compliant: ${report.compliant}\n`;
        csv += `Non-Compliant: ${report.nonCompliant}\n`;
        csv += `Average Score: ${report.averageScore}%\n\n`;
        csv += 'Document,Status,Score\n';

        report.details.forEach(detail => {
            csv += `${detail.documentName},${detail.overallStatus},${detail.complianceScore}%\n`;
        });

        return csv;
    };

    const downloadReport = (csv, filename) => {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
    };

    return (
        <div className="compliance-checker">
            <div className="compliance-header">
                <h2>Compliance Checker</h2>
                <p>Verify document compliance with shipping and logistics regulations</p>
            </div>

            <div className="compliance-rules">
                <h3>Compliance Rules</h3>
                <div className="rules-grid">
                    {complianceRules.map(rule => (
                        <div key={rule.id} className={`rule-card ${rule.required ? 'required' : 'optional'}`}>
                            <div className="rule-icon">{rule.icon}</div>
                            <div className="rule-name">{rule.name}</div>
                            <div className="rule-type">{rule.required ? ' Required' : ' Optional'}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="document-selection">
                <h3>Select Documents to Check</h3>
                <div className="doc-selection-list">
                    {availableDocuments.map(doc => (
                        <label key={doc.id} className="doc-checkbox">
                            <input
                                type="checkbox"
                                checked={selectedDocuments.includes(doc.id)}
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setSelectedDocuments([...selectedDocuments, doc.id]);
                                    } else {
                                        setSelectedDocuments(selectedDocuments.filter(id => id !== doc.id));
                                    }
                                }}
                            />
                            <span className="doc-label">
                                <span className="doc-icon">{doc.type === 'bill_of_lading' ? '' : ''}</span>
                                {doc.name}
                            </span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="compliance-actions">
                <button
                    className="check-btn"
                    onClick={runComplianceCheck}
                    disabled={selectedDocuments.length === 0 || checkStatus === 'checking'}
                >
                    {checkStatus === 'checking' ? ' Checking...' : ' Run Compliance Check'}
                </button>

                {complianceResults.length > 0 && (
                    <button className="report-btn" onClick={generateComplianceReport}>
                         Generate Report
                    </button>
                )}
            </div>

            {checkStatus === 'completed' && complianceResults.length > 0 && (
                <div className="compliance-results">
                    <h3>Compliance Results</h3>
                    <div className="results-summary">
                        <div className="summary-card compliant">
                            <div className="summary-value">
                                {complianceResults.filter(r => r.overallStatus === 'compliant').length}
                            </div>
                            <div className="summary-label">Compliant Documents</div>
                        </div>
                        <div className="summary-card non-compliant">
                            <div className="summary-value">
                                {complianceResults.filter(r => r.overallStatus === 'non-compliant').length}
                            </div>
                            <div className="summary-label">Non-Compliant Documents</div>
                        </div>
                        <div className="summary-card average">
                            <div className="summary-value">
                                {Math.round(
                                    complianceResults.reduce((sum, r) => sum + r.complianceScore, 0) / complianceResults.length
                                )}%
                            </div>
                            <div className="summary-label">Average Score</div>
                        </div>
                    </div>

                    <div className="results-details">
                        {complianceResults.map(result => (
                            <div key={result.documentId} className="result-item">
                                <div className="result-header">
                                    <span className="doc-name">{result.documentName}</span>
                                    <span className={`status-badge ${result.overallStatus}`}>
                                        {result.overallStatus === 'compliant' ? ' Compliant' : ' Non-Compliant'}
                                    </span>
                                    <span className="score">{result.complianceScore}%</span>
                                </div>

                                <div className="result-checks">
                                    {result.results.map(check => (
                                        <div key={check.ruleId} className={`check-item ${check.status}`}>
                                            <span className="check-icon">
                                                {check.status === 'pass' ? '' : ''}
                                            </span>
                                            <span className="check-name">{check.ruleName}</span>
                                            {!check.required && (
                                                <span className="check-type">Optional</span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="compliance-history">
                <h3>Compliance Checks History</h3>
                {complianceChecks.length === 0 ? (
                    <p className="empty-message">No compliance checks performed yet</p>
                ) : (
                    <div className="history-list">
                        {complianceChecks.map(check => (
                            <div key={check.documentId} className="history-item">
                                <div className="item-header">
                                    <span className="doc-name">{check.documentName}</span>
                                    <span className={`status-badge ${check.overallStatus}`}>
                                        {check.overallStatus}
                                    </span>
                                    <span className="score">{check.complianceScore}%</span>
                                </div>
                                <div className="item-date">{new Date(check.checkDate).toLocaleString()}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ComplianceChecker;
