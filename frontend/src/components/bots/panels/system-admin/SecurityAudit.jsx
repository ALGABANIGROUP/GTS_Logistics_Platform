// src/components/bots/panels/system-admin/SecurityAudit.jsx
import React, { useEffect, useState } from 'react';
import {
    Activity,
    BellRing,
    CheckCircle2,
    ClipboardCheck,
    Clock,
    Database,
    FileText,
    KeyRound,
    Lock,
    Shield,
    ShieldCheck
} from 'lucide-react';
import { adminService } from '../../../../services/adminService';
import './SecurityAudit.css';

const SecurityAudit = ({ onNewNotification, refreshKey }) => {
    const [auditLogs, setAuditLogs] = useState([]);
    const [securityAlerts, setSecurityAlerts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [investigatingAlert, setInvestigatingAlert] = useState(null);
    const [filters, setFilters] = useState({
        action: '',
        start_date: '',
        end_date: '',
        user_id: ''
    });

    useEffect(() => {
        loadSecurityData();
    }, [refreshKey, filters]);

    const loadSecurityData = async () => {
        setLoading(true);
        try {
            // Get security data from Security Bot (new data source)
            const [logsFromBot, alertsFromBot, recommendationsFromBot] = await Promise.all([
                adminService.getAuditLogsFromSecurityBot(filters),
                adminService.getSecurityAlertsFromSecurityBot(),
                adminService.getSecurityRecommendationsFromSecurityBot()
            ]);

            // Fallback to original if security bot fails
            if (logsFromBot.error || alertsFromBot.error) {
                console.warn('Security bot unavailable, using original source');
                const [logs, alerts] = await Promise.all([
                    adminService.getAuditLogs(filters),
                    adminService.getSecurityAlerts()
                ]);
                setAuditLogs(logs.logs || []);
                setSecurityAlerts(alerts.alerts || []);
            } else {
                setAuditLogs(logsFromBot.logs || []);
                setSecurityAlerts(alertsFromBot.alerts || []);
            }
        } catch (error) {
            console.error('Failed to load security data:', error);
            onNewNotification?.('Failed to load security data', '!');
        } finally {
            setLoading(false);
        }
    };

    const getAuditCellValue = (log, keys, fallback = 'N/A') => {
        for (const key of keys) {
            if (log?.[key] !== undefined && log?.[key] !== null && String(log[key]).trim() !== '') {
                return String(log[key]);
            }
        }
        return fallback;
    };

    const handleInvestigateAlert = (alert, index) => {
        const nextActionFilter = getAuditCellValue(alert, ['action', 'type', 'title', 'severity'], '');
        setInvestigatingAlert(index);
        if (nextActionFilter) {
            setFilters((current) => ({ ...current, action: nextActionFilter }));
        }
        onNewNotification?.(`Investigating ${alert.title || 'security alert'}`, '!');
    };

    const handleDismissAlert = (index) => {
        const dismissedAlert = securityAlerts[index];
        setSecurityAlerts((current) => current.filter((_, currentIndex) => currentIndex !== index));
        if (investigatingAlert === index) {
            setInvestigatingAlert(null);
        }
        onNewNotification?.(`Dismissed ${dismissedAlert?.title || 'security alert'}`, '');
    };

    const handleExportLogs = () => {
        if (!auditLogs.length) {
            onNewNotification?.('No audit logs available to export', 'i');
            return;
        }

        const header = ['time', 'user', 'action', 'details'];
        const rows = auditLogs.map((log) => [
            getAuditCellValue(log, ['time', 'timestamp', 'created_at']),
            getAuditCellValue(log, ['user_id', 'user', 'email']),
            getAuditCellValue(log, ['action', 'event', 'title']),
            getAuditCellValue(log, ['details', 'description', 'message']),
        ]);
        const csvContent = [header, ...rows]
            .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
            .join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `security-audit-${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        onNewNotification?.(`Exported ${auditLogs.length} audit logs`, '');
    };

    const getSeverityColor = (severity) => {
        const colors = {
            critical: '#ef4444',
            high: '#f97316',
            medium: '#eab308',
            low: '#3b82f6',
            info: '#64748b'
        };

        return colors[severity] || colors.info;
    };

    const securityStats = [
        { id: 'status', label: 'System Status', value: 'Secured', icon: Shield },
        { id: 'alerts', label: 'Active Alerts', value: securityAlerts.length, icon: BellRing },
        { id: 'logs', label: 'Audit Logs', value: auditLogs.length, icon: FileText },
        { id: 'monitor', label: 'Monitoring', value: 'Enabled', icon: Activity }
    ];

    const recommendations = [
        {
            id: 'password',
            title: 'Password Policy',
            description: 'Enforce strong password rules for all users.',
            status: 'implemented',
            icon: ShieldCheck,
            iconClass: 'rec-icon-password'
        },
        {
            id: '2fa',
            title: 'Two-Factor Authentication',
            description: 'Require 2FA for admin and sensitive accounts.',
            status: 'pending',
            icon: KeyRound,
            iconClass: 'rec-icon-2fa'
        },
        {
            id: 'audits',
            title: 'Regular Audits',
            description: 'Review security logs on a weekly schedule.',
            status: 'implemented',
            icon: ClipboardCheck,
            iconClass: 'rec-icon-audits'
        },
        {
            id: 'alerts',
            title: 'Alert System',
            description: 'Notify admins in real time for suspicious activity.',
            status: 'implemented',
            icon: BellRing,
            iconClass: 'rec-icon-alerts'
        },
        {
            id: 'backup',
            title: 'Backup Encryption',
            description: 'Encrypt backups at rest and in transit.',
            status: 'pending',
            icon: Database,
            iconClass: 'rec-icon-backup'
        },
        {
            id: 'ssl',
            title: 'SSL/TLS',
            description: 'Force HTTPS for all connections.',
            status: 'implemented',
            icon: Lock,
            iconClass: 'rec-icon-ssl'
        }
    ];

    const statusLabels = {
        implemented: 'Implemented',
        pending: 'Pending'
    };

    const auditFeatureList = [
        'All user login/logout activities',
        'Data modification tracking',
        'Permission changes',
        'Critical operations logging',
        'Security event monitoring',
        'Export to CSV/PDF'
    ];

    const checklistItems = [
        { id: 'db-encryption', text: 'Database encryption enabled', status: 'completed' },
        { id: 'api-auth', text: 'API authentication required', status: 'completed' },
        { id: 'rbac', text: 'Role-based access control', status: 'completed' },
        { id: 'ids', text: 'Intrusion detection system', status: 'pending' },
        { id: 'updates', text: 'Regular security updates', status: 'completed' },
        { id: 'pentest', text: 'Penetration testing', status: 'pending' }
    ];

    return (
        <div className="security-audit">
            <div className="security-overview">
                <h2>Security Overview</h2>
                <div className="security-stats">
                    {securityStats.map((stat) => {
                        const Icon = stat.icon;
                        return (
                            <div key={stat.id} className="security-stat-card">
                                <span className="stat-icon-security">
                                    <Icon />
                                </span>
                                <div className="stat-content-security">
                                    <span className="stat-value-security">{stat.value}</span>
                                    <span className="stat-label-security">{stat.label}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {securityAlerts.length > 0 && (
                <div className="alerts-section">
                    <h3>Security Alerts</h3>
                    <div className="alerts-grid">
                        {securityAlerts.map((alert, index) => (
                            <div
                                key={index}
                                className="alert-card"
                                style={{ borderLeftColor: getSeverityColor(alert.severity) }}
                            >
                                <div className="alert-header">
                                    <span
                                        className="severity-badge"
                                        style={{ background: getSeverityColor(alert.severity) }}
                                    >
                                        {alert.severity}
                                    </span>
                                    <span className="alert-time">{alert.time}</span>
                                </div>
                                <h4 className="alert-title">{alert.title}</h4>
                                <p className="alert-description">{alert.description}</p>
                                {investigatingAlert === index ? (
                                    <p className="alert-description">Investigation in progress. Audit filters were updated for this alert.</p>
                                ) : null}
                                <div className="alert-actions">
                                    <button
                                        type="button"
                                        className="btn-alert-action"
                                        onClick={() => handleInvestigateAlert(alert, index)}
                                    >
                                        Investigate
                                    </button>
                                    <button
                                        type="button"
                                        className="btn-alert-action dismiss"
                                        onClick={() => handleDismissAlert(index)}
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="audit-logs-section">
                <div className="section-header">
                    <h3>Audit Logs</h3>
                    <button className="btn-export" onClick={handleExportLogs}>
                        Export Logs
                    </button>
                </div>

                <div className="audit-filters">
                    <input
                        type="text"
                        placeholder="User ID"
                        value={filters.user_id}
                        onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
                        className="filter-input"
                    />
                    <input
                        type="text"
                        placeholder="Action"
                        value={filters.action}
                        onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                        className="filter-input"
                    />
                    <input
                        type="date"
                        value={filters.start_date}
                        onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                        className="filter-input"
                    />
                    <input
                        type="date"
                        value={filters.end_date}
                        onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                        className="filter-input"
                    />
                    <button
                        className="btn-filter-reset"
                        onClick={() => setFilters({ action: '', start_date: '', end_date: '', user_id: '' })}
                    >
                        Reset Filters
                    </button>
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading audit logs...</p>
                    </div>
                ) : auditLogs.length > 0 ? (
                    <div className="audit-info-box">
                        <h4>Audit Log Results</h4>
                        <div className="checklist-items">
                            {auditLogs.map((log, index) => (
                                <div key={`${getAuditCellValue(log, ['id'], index)}-${index}`} className="checklist-item completed">
                                    <span className="check-text">
                                        <strong>{getAuditCellValue(log, ['action', 'event', 'title'])}</strong>
                                        {' · '}
                                        {getAuditCellValue(log, ['user_id', 'user', 'email'])}
                                        {' · '}
                                        {getAuditCellValue(log, ['time', 'timestamp', 'created_at'])}
                                        {' · '}
                                        {getAuditCellValue(log, ['details', 'description', 'message'])}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="audit-info-box">
                        <h4>Audit Log System</h4>
                        <p>No audit log entries matched the current filters. Security monitoring is active and ready to export when logs are available.</p>
                        <ul className="features-list">
                            {auditFeatureList.map((feature) => (
                                <li key={feature}>{feature}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            <div className="security-recommendations">
                <h3>Security Recommendations</h3>
                <div className="recommendations-grid">
                    {recommendations.map((item) => {
                        const Icon = item.icon;
                        return (
                            <div key={item.id} className="recommendation-card">
                                <span className={`rec-icon ${item.iconClass}`}>
                                    <Icon />
                                </span>
                                <h4>{item.title}</h4>
                                <p>{item.description}</p>
                                <span className={`rec-status ${item.status}`}>
                                    {statusLabels[item.status]}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="security-checklist">
                <h3>Security Checklist</h3>
                <div className="checklist-items">
                    {checklistItems.map((item) => {
                        const Icon = item.status === 'completed' ? CheckCircle2 : Clock;
                        return (
                            <div key={item.id} className={`checklist-item ${item.status}`}>
                                <span className="check-icon">
                                    <Icon />
                                </span>
                                <span className="check-text">{item.text}</span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default SecurityAudit;
