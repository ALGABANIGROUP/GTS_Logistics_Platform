// src/components/bots/panels/documents-manager/DocumentsManagerPanel.jsx
import React, { useState, useEffect } from 'react';
import DocumentsDashboard from './DocumentsDashboard';
import DocumentUploader from './DocumentUploader';
import DocumentLibrary from './DocumentLibrary';
import OCRProcessor from './OCRProcessor';
import ComplianceChecker from './ComplianceChecker';
import DocumentWorkflow from './DocumentWorkflow';
import SmartRecognition from './SmartRecognition';
import DigitalSigning from './DigitalSigning';
import AdvancedWorkflows from './AdvancedWorkflows';
import AnalyticsDashboard from './AnalyticsDashboard';
import IntegrationsPanel from './IntegrationsPanel';
import SecurityPanel from './SecurityPanel';
import AIAssistant from './AIAssistant';
import documentsService from '../../../../services/documentsService';
import './DocumentsManagerPanel.css';

const DocumentsManagerPanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [botConfig, setBotConfig] = useState(null);
    const [docStats, setDocStats] = useState({
        total: 0,
        processed: 0,
        pending: 0,
        storage: '0 MB'
    });

    useEffect(() => {
        const config = {
            name: "AI Documents Manager",
            description: "Intelligent document management system for shipping and logistics",
            status: "active",
            version: "1.0.0",
            lastUpdated: new Date().toISOString().split('T')[0],

            tabs: [
                { id: 'dashboard', name: 'Dashboard', icon: '' },
                { id: 'upload', name: 'Upload Documents', icon: '' },
                { id: 'library', name: 'Document Library', icon: '' },
                { id: 'ocr', name: 'OCR Processing', icon: '' },
                { id: 'compliance', name: 'Compliance Check', icon: '' },
                { id: 'workflow', name: 'Workflows', icon: '' },
                { id: 'smart-recognition', name: 'Smart Recognition', icon: '' },
                { id: 'digital-signing', name: 'Digital Signing', icon: '' },
                { id: 'advanced-workflows', name: 'Advanced Workflows', icon: '' },
                { id: 'analytics', name: 'Analytics', icon: '' },
                { id: 'integrations', name: 'Integrations', icon: '' },
                { id: 'security', name: 'Security', icon: '' },
                { id: 'ai-assistant', name: 'AI Assistant', icon: '' },
                { id: 'reports', name: 'Reports', icon: '' },
                { id: 'settings', name: 'Settings', icon: '' }
            ],

            quickStats: [
                { label: 'Total Documents', value: '0', icon: '', trend: '0' },
                { label: 'Processed Today', value: '0', icon: '', trend: '0' },
                { label: 'Storage Used', value: '0 MB', icon: '', trend: '0%' },
                { label: 'Compliance Rate', value: '0%', icon: '', trend: '0%' }
            ]
        };

        setBotConfig(config);
        loadDashboardSummary();
    }, []);

    const loadDashboardSummary = async () => {
        try {
            const dashboard = await documentsService.getDashboard();
            const stats = dashboard.stats || {};
            setDocStats({
                total: stats.total || 0,
                processed: stats.processed || 0,
                pending: stats.pending || 0,
                storage: stats.storage || '0 MB'
            });
            setBotConfig(prev => prev ? ({
                ...prev,
                quickStats: [
                    { label: 'Total Documents', value: String(stats.total || 0), icon: '', trend: '' },
                    { label: 'Processed', value: String(stats.processed || 0), icon: '', trend: '' },
                    { label: 'Storage Used', value: stats.storage || '0 MB', icon: '', trend: '' },
                    { label: 'Pending Signatures', value: String(stats.pendingSignatures || 0), icon: '', trend: '' }
                ]
            }) : prev);
        } catch (error) {
            console.error('Failed to load documents dashboard summary:', error);
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <DocumentsDashboard stats={docStats} />;
            case 'upload':
                return <DocumentUploader onUploadSuccess={() => updateStats()} />;
            case 'library':
                return <DocumentLibrary />;
            case 'ocr':
                return <OCRProcessor />;
            case 'compliance':
                return <ComplianceChecker />;
            case 'workflow':
                return <DocumentWorkflow />;
            case 'smart-recognition':
                return <SmartRecognition />;
            case 'digital-signing':
                return <DigitalSigning />;
            case 'advanced-workflows':
                return <AdvancedWorkflows />;
            case 'analytics':
                return <AnalyticsDashboard />;
            case 'integrations':
                return <IntegrationsPanel />;
            case 'security':
                return <SecurityPanel />;
            case 'ai-assistant':
                return <AIAssistant />;
            case 'reports':
                return <div className="section-card"><h3> Reports</h3><p>Reports feature coming soon</p></div>;
            case 'settings':
                return <div className="section-card"><h3> Settings</h3><p>Settings feature coming soon</p></div>;
            default:
                return <DocumentsDashboard stats={docStats} />;
        }
    };

    const updateStats = () => {
        loadDashboardSummary();
    };

    if (!botConfig) return <div>Loading Documents Manager...</div>;

    return (
        <div className="documents-manager-panel">
            <div className="panel-header">
                <div className="header-content">
                    <h1> {botConfig.name}</h1>
                    <p className="description">{botConfig.description}</p>
                    <div className="header-meta">
                        <span className={`status-badge ${botConfig.status}`}>
                            {botConfig.status === 'active' ? '' : ''} {botConfig.status}
                        </span>
                        <span className="version">v{botConfig.version}</span>
                        <span className="updated">Updated: {botConfig.lastUpdated}</span>
                    </div>
                </div>
            </div>

            <div className="quick-stats-bar">
                {botConfig.quickStats.map((stat, index) => (
                    <div key={index} className="quick-stat-card">
                        <span className="stat-icon">{stat.icon}</span>
                        <div className="stat-content">
                            <div className="stat-label">{stat.label}</div>
                            <div className="stat-value">{stat.value}</div>
                            {stat.trend && (
                                <div className="stat-trend">
                                    {parseFloat(stat.trend) > 0 ? '' : ''} {stat.trend}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="tabs-navigation">
                {botConfig.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span className="tab-name">{tab.name}</span>
                    </button>
                ))}
            </div>

            <div className="tab-content">
                {renderTabContent()}
            </div>
        </div>
    );
};

export default DocumentsManagerPanel;
