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
                                <div className="alert-actions">
                                    <button className="btn-alert-action">Investigate</button>
                                    <button className="btn-alert-action dismiss">Dismiss</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="audit-logs-section">
                <div className="section-header">
                    <h3>Audit Logs</h3>
                    <button
                        className="btn-export"
                        onClick={() => onNewNotification?.('Export feature coming soon', 'i')}
                    >
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
                ) : (
                    <div className="audit-info-box">
                        <h4>Audit Log System</h4>
                        <p>The comprehensive audit logging system is currently under development and will include:</p>
                        <ul className="features-list">
                            {auditFeatureList.map((feature) => (
                                <li key={feature}>{feature}</li>
                            ))}
                        </ul>
                        <p className="info-note">
                            <strong>Note:</strong> Backend endpoints for audit logging need to be implemented at
                            <code>/admin/users/audit/logs</code> and <code>/admin/security/alerts</code>
                        </p>
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
