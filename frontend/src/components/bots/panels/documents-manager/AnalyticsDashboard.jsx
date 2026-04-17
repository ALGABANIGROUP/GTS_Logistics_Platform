// src/components/bots/panels/documents-manager/AnalyticsDashboard.jsx
import React, { useState } from 'react';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
    const [timeRange, setTimeRange] = useState('7days'); // 7days, 30days, 90days, 1year
    const [selectedMetric, setSelectedMetric] = useState('all');

    const metrics = [
        { label: 'Total Documents', value: 15847, change: '+12.5%', trend: 'up' },
        { label: 'Documents Processed', value: 12456, change: '+8.3%', trend: 'up' },
        { label: 'Processing Rate', value: '98.5%', change: '+2.1%', trend: 'up' },
        { label: 'Avg Processing Time', value: '2.3h', change: '-15.2%', trend: 'down' }
    ];

    const documentTypeData = [
        { type: 'Bill of Lading', count: 4250, percentage: 26.8, color: '#3b82f6' },
        { type: 'Commercial Invoice', count: 3890, percentage: 24.6, color: '#10b981' },
        { type: 'Packing List', count: 3120, percentage: 19.7, color: '#f59e0b' },
        { type: 'Customs Declaration', count: 2450, percentage: 15.5, color: '#8b5cf6' },
        { type: 'Insurance Certificate', count: 1247, percentage: 7.9, color: '#ef4444' },
        { type: 'Other', count: 890, percentage: 5.5, color: '#6366f1' }
    ];

    const ocrAccuracy = [
        { model: 'BOL Model v2.1', accuracy: 97.5, samples: 1250 },
        { model: 'Invoice Model v2.0', accuracy: 95.8, samples: 980 },
        { model: 'Customs Model v1.8', accuracy: 93.2, samples: 750 },
        { model: 'Insurance Model v1.5', accuracy: 91.4, samples: 520 }
    ];

    const complianceData = [
        { name: 'Compliant', value: 14220, percentage: 89.8, color: '#10b981' },
        { name: 'Non-Compliant', value: 987, percentage: 6.2, color: '#ef4444' },
        { name: 'Requires Review', value: 640, percentage: 4.0, color: '#f59e0b' }
    ];

    const anomalies = [
        {
            id: 1,
            type: 'Unusual Document Size',
            severity: 'medium',
            count: 15,
            description: 'Files significantly larger than average',
            firstDetected: '2024-01-15 10:30'
        },
        {
            id: 2,
            type: 'OCR Processing Failure',
            severity: 'high',
            count: 23,
            description: 'Unable to process specific document formats',
            firstDetected: '2024-01-15 08:45'
        },
        {
            id: 3,
            type: 'Compliance Violations',
            severity: 'medium',
            count: 8,
            description: 'Documents missing required fields',
            firstDetected: '2024-01-14 16:20'
        }
    ];

    const recommendations = [
        {
            id: 1,
            title: 'Retrain BOL Model',
            description: 'Current model accuracy is dropping. Recommended to retrain with new samples.',
            priority: 'high',
            action: 'Start Training'
        },
        {
            id: 2,
            title: 'Optimize Workflow Performance',
            description: 'Express Import workflow is taking longer. Consider adjusting processing order.',
            priority: 'medium',
            action: 'Review Settings'
        },
        {
            id: 3,
            title: 'Increase OCR Language Support',
            description: 'Detected 45 documents in Chinese. Consider adding Chinese language support.',
            priority: 'low',
            action: 'Add Language'
        }
    ];

    const performanceTrends = [
        { date: '2024-01-10', processed: 450, successful: 445, failed: 5 },
        { date: '2024-01-11', processed: 480, successful: 475, failed: 5 },
        { date: '2024-01-12', processed: 520, successful: 515, failed: 5 },
        { date: '2024-01-13', processed: 490, successful: 485, failed: 5 },
        { date: '2024-01-14', processed: 510, successful: 505, failed: 5 },
        { date: '2024-01-15', processed: 540, successful: 535, failed: 5 }
    ];

    return (
        <div className="analytics-dashboard">
            <div className="analytics-header">
                <h2> Advanced Analytics & Insights</h2>
                <p>Real-time document processing analytics with predictive insights</p>
            </div>

            {/* Time Range Selector */}
            <div className="time-range-selector">
                <button
                    className={`range-btn ${timeRange === '7days' ? 'active' : ''}`}
                    onClick={() => setTimeRange('7days')}
                >
                    Last 7 Days
                </button>
                <button
                    className={`range-btn ${timeRange === '30days' ? 'active' : ''}`}
                    onClick={() => setTimeRange('30days')}
                >
                    Last 30 Days
                </button>
                <button
                    className={`range-btn ${timeRange === '90days' ? 'active' : ''}`}
                    onClick={() => setTimeRange('90days')}
                >
                    Last 90 Days
                </button>
                <button
                    className={`range-btn ${timeRange === '1year' ? 'active' : ''}`}
                    onClick={() => setTimeRange('1year')}
                >
                    1 Year
                </button>
            </div>

            {/* Key Metrics */}
            <div className="key-metrics">
                <h3> Key Performance Metrics</h3>
                <div className="metrics-grid">
                    {metrics.map((metric, idx) => (
                        <div key={idx} className="metric-card">
                            <div className="metric-label">{metric.label}</div>
                            <div className="metric-value">{metric.value}</div>
                            <div className={`metric-change ${metric.trend}`}>
                                {metric.trend === 'up' ? '' : ''} {metric.change}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Document Type Distribution */}
            <div className="document-distribution">
                <h3> Document Type Distribution</h3>
                <div className="distribution-container">
                    <div className="chart-panel">
                        <div className="pie-chart">
                            {documentTypeData.map((item, idx) => (
                                <div key={idx} className="pie-segment" style={{
                                    background: item.color,
                                    width: `${item.percentage}%`
                                }}>
                                    {item.percentage > 10 && <span>{item.percentage}%</span>}
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="distribution-legend">
                        {documentTypeData.map((item, idx) => (
                            <div key={idx} className="legend-item">
                                <span className="legend-color" style={{ backgroundColor: item.color }}></span>
                                <div className="legend-text">
                                    <div className="legend-label">{item.type}</div>
                                    <div className="legend-value">{item.count.toLocaleString()} ({item.percentage}%)</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* OCR Model Performance */}
            <div className="ocr-performance">
                <h3> OCR Model Accuracy Comparison</h3>
                <div className="performance-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Model</th>
                                <th>Accuracy</th>
                                <th>Training Samples</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ocrAccuracy.map((model, idx) => (
                                <tr key={idx}>
                                    <td>{model.model}</td>
                                    <td>
                                        <div className="accuracy-bar">
                                            <div className="bar-fill" style={{ width: `${model.accuracy}%` }}>
                                                {model.accuracy.toFixed(1)}%
                                            </div>
                                        </div>
                                    </td>
                                    <td>{model.samples.toLocaleString()}</td>
                                    <td>
                                        <span className="status-badge">
                                            {model.accuracy > 95 ? ' Excellent' : model.accuracy > 90 ? ' Good' : ' Needs Review'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Compliance Status */}
            <div className="compliance-status">
                <h3> Compliance Status Overview</h3>
                <div className="compliance-container">
                    <div className="compliance-chart">
                        <div className="donut-chart">
                            {complianceData.map((item, idx, arr) => {
                                const startAngle = arr.slice(0, idx).reduce((sum, d) => sum + (d.percentage * 3.6), 0);
                                return (
                                    <div
                                        key={idx}
                                        className="donut-segment"
                                        style={{
                                            background: item.color,
                                            width: '100%',
                                            height: '20px',
                                            marginBottom: '5px',
                                            borderRadius: '4px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            paddingLeft: '10px',
                                            color: 'white',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        {item.name}: {item.percentage}%
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                    <div className="compliance-stats">
                        {complianceData.map((item, idx) => (
                            <div key={idx} className="compliance-stat">
                                <div className="stat-color" style={{ backgroundColor: item.color }}></div>
                                <div className="stat-info">
                                    <div className="stat-title">{item.name}</div>
                                    <div className="stat-numbers">{item.value.toLocaleString()} documents</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Anomaly Detection */}
            <div className="anomalies-section">
                <h3> Anomaly Detection</h3>
                <div className="anomalies-list">
                    {anomalies.map(anomaly => (
                        <div key={anomaly.id} className={`anomaly-card severity-${anomaly.severity}`}>
                            <div className="anomaly-icon">
                                {anomaly.severity === 'high' ? '' : anomaly.severity === 'medium' ? '' : ''}
                            </div>
                            <div className="anomaly-content">
                                <div className="anomaly-title">{anomaly.type}</div>
                                <div className="anomaly-description">{anomaly.description}</div>
                                <div className="anomaly-meta">
                                    <span className="anomaly-count">{anomaly.count} instances</span>
                                    <span className="anomaly-detected">Detected: {anomaly.firstDetected}</span>
                                </div>
                            </div>
                            <div className="anomaly-action">
                                <button className="action-btn">Investigate</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* AI Recommendations */}
            <div className="recommendations-section">
                <h3> AI-Powered Recommendations</h3>
                <div className="recommendations-list">
                    {recommendations.map(rec => (
                        <div key={rec.id} className={`recommendation-card priority-${rec.priority}`}>
                            <div className="rec-priority">
                                {rec.priority === 'high' ? '' : rec.priority === 'medium' ? '' : ''}
                            </div>
                            <div className="rec-content">
                                <div className="rec-title">{rec.title}</div>
                                <div className="rec-description">{rec.description}</div>
                            </div>
                            <button className="rec-action">{rec.action}</button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Performance Trends Chart */}
            <div className="performance-trends">
                <h3> Performance Trends</h3>
                <div className="trends-chart">
                    <div className="chart-container">
                        <div className="chart-header">
                            <span>Daily Processing Performance</span>
                        </div>
                        <div className="mini-chart">
                            <div className="chart-bars">
                                {performanceTrends.map((day, idx) => (
                                    <div key={idx} className="bar-group">
                                        <div className="bar" style={{ height: `${(day.processed / 600) * 100}%` }}>
                                            <span className="bar-value">{day.processed}</span>
                                        </div>
                                        <div className="bar-label">{day.date.split('-')[2]}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Export Options */}
            <div className="export-section">
                <h3> Export Analytics</h3>
                <div className="export-buttons">
                    <button className="export-btn"> Export as PDF</button>
                    <button className="export-btn"> Export as CSV</button>
                    <button className="export-btn"> Email Report</button>
                    <button className="export-btn"> Share Link</button>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
