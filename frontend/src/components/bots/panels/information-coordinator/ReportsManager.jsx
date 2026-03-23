// Reports Manager Component
import React, { useState, useEffect } from 'react';
import informationService from '../../../../services/informationService';
import './OperationalDashboard.css';

const ReportsManager = ({ onNewNotification, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [reports, setReports] = useState([]);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newReport, setNewReport] = useState({
        type: 'shipments',
        startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0],
        format: 'json'
    });

    useEffect(() => {
        loadReports();
    }, [refreshKey]);

    const loadReports = async () => {
        setLoading(true);
        try {
            const data = await informationService.listReports();
            setReports(data.reports || []);
        } catch (error) {
            onNewNotification?.('Failed to load reports', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateReport = async () => {
        setLoading(true);
        try {
            const result = await informationService.generateCustomReport(
                newReport.type,
                newReport.startDate,
                newReport.endDate,
                {},
                newReport.format
            );

            if (result.status === 'success') {
                onNewNotification?.('Report generated successfully', 'success');
                setShowCreateForm(false);
                loadReports();
            } else {
                onNewNotification?.('Failed to generate report', 'error');
            }
        } catch (error) {
            onNewNotification?.('Error generating report', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReport = async (reportId) => {
        const result = await informationService.downloadReport(reportId, 'pdf');
        if (result.status === 'success') {
            onNewNotification?.('Report downloaded successfully', 'success');
        } else {
            onNewNotification?.('Failed to download report', 'error');
        }
    };

    const handleDeleteReport = async (reportId) => {
        if (confirm('Are you sure you want to delete this report?')) {
            const result = await informationService.deleteReport(reportId);
            if (result.status === 'success') {
                onNewNotification?.('Report deleted successfully', 'success');
                loadReports();
            } else {
                onNewNotification?.('Failed to delete report', 'error');
            }
        }
    };

    return (
        <div className="reports-manager">
            {/* Reports Header */}
            <div className="reports-header">
                <div>
                    <h2> Reports Manager</h2>
                    <p>Generate, manage, and download custom reports</p>
                </div>
                <button
                    onClick={() => setShowCreateForm(true)}
                    className="create-report-button"
                >
                    + New Report
                </button>
            </div>

            {/* Create Report Form */}
            {showCreateForm && (
                <div className="create-report-modal">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3>Generate Custom Report</h3>
                            <button
                                onClick={() => setShowCreateForm(false)}
                                className="close-button"
                            >
                                
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="form-group">
                                <label>Report Type</label>
                                <select
                                    value={newReport.type}
                                    onChange={(e) => setNewReport({ ...newReport, type: e.target.value })}
                                    className="form-input"
                                >
                                    <option value="shipments">Shipments</option>
                                    <option value="invoices">Invoices</option>
                                    <option value="customers">Customers</option>
                                    <option value="inventory">Inventory</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Start Date</label>
                                <input
                                    type="date"
                                    value={newReport.startDate}
                                    onChange={(e) => setNewReport({ ...newReport, startDate: e.target.value })}
                                    className="form-input"
                                />
                            </div>
                            <div className="form-group">
                                <label>End Date</label>
                                <input
                                    type="date"
                                    value={newReport.endDate}
                                    onChange={(e) => setNewReport({ ...newReport, endDate: e.target.value })}
                                    className="form-input"
                                />
                            </div>
                            <div className="form-group">
                                <label>Format</label>
                                <select
                                    value={newReport.format}
                                    onChange={(e) => setNewReport({ ...newReport, format: e.target.value })}
                                    className="form-input"
                                >
                                    <option value="json">JSON</option>
                                    <option value="pdf">PDF</option>
                                    <option value="csv">CSV</option>
                                    <option value="excel">Excel</option>
                                </select>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button
                                onClick={() => setShowCreateForm(false)}
                                className="cancel-button"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleGenerateReport}
                                className="generate-button"
                                disabled={loading}
                            >
                                {loading ? 'Generating...' : 'Generate Report'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Reports List */}
            {loading && reports.length === 0 ? (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading reports...</p>
                </div>
            ) : reports.length > 0 ? (
                <div className="reports-list">
                    {reports.map(report => (
                        <div key={report.id} className="report-item">
                            <div className="report-icon"></div>
                            <div className="report-info">
                                <h4 className="report-name">{report.name || `Report ${report.id}`}</h4>
                                <div className="report-meta">
                                    <span>Type: {report.type}</span>
                                    <span></span>
                                    <span>Created: {new Date(report.created_at).toLocaleDateString()}</span>
                                    <span></span>
                                    <span>Format: {report.format}</span>
                                </div>
                            </div>
                            <div className="report-actions">
                                <button
                                    onClick={() => handleDownloadReport(report.id)}
                                    className="download-button"
                                    title="Download"
                                >
                                    
                                </button>
                                <button
                                    onClick={() => handleDeleteReport(report.id)}
                                    className="delete-button"
                                    title="Delete"
                                >
                                    
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <span className="empty-icon"></span>
                    <p>No reports yet</p>
                    <p className="empty-hint">Click "New Report" to generate your first report</p>
                </div>
            )}

            {/* Backend Integration Note */}
            <div className="integration-note">
                <span className="note-icon"></span>
                <p>Backend integration required for full report generation and storage functionality.</p>
            </div>
        </div>
    );
};

export default ReportsManager;
