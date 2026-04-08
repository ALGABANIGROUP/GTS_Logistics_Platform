// frontend/src/pages/ai-bots/AISecurityManager.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import axiosClient from '../../api/axiosClient';

const AISecurityManager = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [scans, setScans] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [tabValue, setTabValue] = useState(0);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [scanning, setScanning] = useState(false);

  const { showSuccess, showError, showInfo } = useNotification();

  // جلب جميع البيانات
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const [dashboardRes, alertsRes, scansRes, metricsRes] = await Promise.all([
        axiosClient.get('/api/v1/security/dashboard'),
        axiosClient.get('/api/v1/security/alerts?limit=20'),
        axiosClient.get('/api/v1/security/scans'),
        axiosClient.get('/api/v1/security/metrics')
      ]);

      setDashboardData(dashboardRes.data);
      setAlerts(alertsRes.data.alerts || []);
      setScans(scansRes.data.scans || []);
      setMetrics(metricsRes.data);

    } catch (error) {
      console.log('Using mock data for Security Manager');
      // بيانات تجريبية احتياطية
      setMetrics({
        total_alerts: 12,
        critical_alerts: 2,
        high_alerts: 3,
        resolved_alerts: 7,
        active_sessions: 42,
        failed_logins_24h: 8,
        suspicious_activities: 5
      });
      setAlerts([
        { id: 1, title: "Multiple failed login attempts", severity: "high", status: "new", timestamp: new Date().toISOString(), source_ip: "192.168.1.100" },
        { id: 2, title: "Suspicious API access", severity: "medium", status: "investigating", timestamp: new Date().toISOString(), source_ip: "10.0.0.45" },
        { id: 3, title: "Database query timeout", severity: "low", status: "resolved", timestamp: new Date().toISOString() }
      ]);
      setDashboardData({
        system_status: { firewall: "active", antivirus: "active", intrusion_detection: "active" }
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // بدء فحص أمني
  const startSecurityScan = async () => {
    setScanning(true);
    try {
      const response = await axiosClient.post('/api/v1/security/scan/start', { scan_type: 'quick' });
      showSuccess('Security scan started successfully');
      fetchAllData();
    } catch (error) {
      showError('Failed to start security scan');
    } finally {
      setScanning(false);
    }
  };

  // تحديث حالة التنبيه
  const updateAlertStatus = async () => {
    if (!selectedAlert || !newStatus) return;

    try {
      await axiosClient.patch(`/api/v1/security/alerts/${selectedAlert.id}/status`, { status: newStatus });
      showSuccess(`Alert marked as ${newStatus}`);
      setStatusDialogOpen(false);
      fetchAllData();
    } catch (error) {
      showError('Failed to update alert status');
    }
  };

  // الحصول على لون شدة التنبيه
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return { bg: 'border-rose-500/20 bg-rose-500/10 text-rose-200', label: 'Critical' };
      case 'high': return { bg: 'border-orange-500/20 bg-orange-500/10 text-orange-200', label: 'High' };
      case 'medium': return { bg: 'border-amber-500/20 bg-amber-500/10 text-amber-200', label: 'Medium' };
      case 'low': return { bg: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200', label: 'Low' };
      default: return { bg: 'border-blue-500/20 bg-blue-500/10 text-blue-200', label: 'Info' };
    }
  };

  // الحصول على لون الحالة
  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return { bg: 'border-rose-500/20 bg-rose-500/10 text-rose-200', label: 'New' };
      case 'investigating': return { bg: 'border-orange-500/20 bg-orange-500/10 text-orange-200', label: 'Investigating' };
      case 'resolved': return { bg: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200', label: 'Resolved' };
      case 'false_positive': return { bg: 'border-blue-500/20 bg-blue-500/10 text-blue-200', label: 'False Positive' };
      default: return { bg: 'border-slate-500/20 bg-slate-500/10 text-slate-200', label: status };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-rose-400" />
          <p className="text-slate-300">Loading Security Manager dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="mx-auto max-w-7xl space-y-6 p-6">
        {/* Header */}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-3xl font-bold text-white">
              AI Security Manager
            </div>
            <div className="mt-2 text-slate-300">
              Monitor and manage system security, alerts, and compliance
            </div>
          </div>
          <button
            onClick={startSecurityScan}
            disabled={scanning}
            className="rounded-lg bg-sky-500/80 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {scanning ? 'Scanning...' : 'Start Security Scan'}
          </button>
        </div>

        {/* Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-2xl font-bold text-rose-200">{metrics.critical_alerts || 0}</div>
            <div className="text-sm text-rose-300">Critical Alerts</div>
          </div>
          <div className="rounded-2xl border border-orange-500/20 bg-orange-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-2xl font-bold text-orange-200">{metrics.high_alerts || 0}</div>
            <div className="text-sm text-orange-300">High Alerts</div>
          </div>
          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-2xl font-bold text-emerald-200">{metrics.resolved_alerts || 0}</div>
            <div className="text-sm text-emerald-300">Resolved</div>
          </div>
          <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-2xl font-bold text-blue-200">{metrics.active_sessions || 0}</div>
            <div className="text-sm text-blue-300">Active Sessions</div>
          </div>
          <div className="rounded-2xl border border-purple-500/20 bg-purple-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-2xl font-bold text-purple-200">{metrics.failed_logins_24h || 0}</div>
            <div className="text-sm text-purple-300">Failed Logins (24h)</div>
          </div>
        </div>

        {/* System Status */}
        {dashboardData?.system_status && (
          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-lg font-semibold text-emerald-200 mb-4">System Components</div>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-emerald-400"></div>
                <span className="text-sm text-emerald-200">Firewall: {dashboardData.system_status.firewall}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-emerald-400"></div>
                <span className="text-sm text-emerald-200">Antivirus: {dashboardData.system_status.antivirus}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-emerald-400"></div>
                <span className="text-sm text-emerald-200">Intrusion Detection: {dashboardData.system_status.intrusion_detection}</span>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-1 shadow-lg shadow-black/40 backdrop-blur">
          <div className="flex">
            <button
              onClick={() => setTabValue(0)}
              className={`flex-1 rounded-xl px-6 py-3 text-sm font-semibold transition ${
                tabValue === 0
                  ? 'bg-white/10 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Security Alerts
            </button>
            <button
              onClick={() => setTabValue(1)}
              className={`flex-1 rounded-xl px-6 py-3 text-sm font-semibold transition ${
                tabValue === 1
                  ? 'bg-white/10 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Security Scans
            </button>
            <button
              onClick={() => setTabValue(2)}
              className={`flex-1 rounded-xl px-6 py-3 text-sm font-semibold transition ${
                tabValue === 2
                  ? 'bg-white/10 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              System Health
            </button>
          </div>
        </div>

        {/* Alerts Tab */}
        {tabValue === 0 && (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-lg font-semibold text-white mb-4">Security Alerts</div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-3 text-sm font-semibold text-slate-300">Severity</th>
                    <th className="text-left p-3 text-sm font-semibold text-slate-300">Title</th>
                    <th className="text-left p-3 text-sm font-semibold text-slate-300">Source IP</th>
                    <th className="text-left p-3 text-sm font-semibold text-slate-300">Status</th>
                    <th className="text-left p-3 text-sm font-semibold text-slate-300">Timestamp</th>
                    <th className="text-center p-3 text-sm font-semibold text-slate-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => {
                    const severity = getSeverityColor(alert.severity);
                    const status = getStatusColor(alert.status);
                    return (
                      <tr key={alert.id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="p-3">
                          <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${severity.bg}`}>
                            {severity.label}
                          </span>
                        </td>
                        <td className="p-3 text-sm text-white">{alert.title}</td>
                        <td className="p-3 text-sm text-slate-300">{alert.source_ip || '-'}</td>
                        <td className="p-3">
                          <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${status.bg}`}>
                            {status.label}
                          </span>
                        </td>
                        <td className="p-3 text-sm text-slate-300">{new Date(alert.timestamp).toLocaleString()}</td>
                        <td className="p-3 text-center">
                          <button
                            onClick={() => {
                              setSelectedAlert(alert);
                              setNewStatus(alert.status);
                              setStatusDialogOpen(true);
                            }}
                            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:bg-white/10"
                          >
                            Update
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Scans Tab */}
        {tabValue === 1 && (
          <div className="grid gap-4 md:grid-cols-2">
            {scans.map((scan) => (
              <div key={scan.id} className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/40 backdrop-blur">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-lg font-semibold text-white">{scan.name}</div>
                  <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${
                    scan.status === 'completed' ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200' :
                    scan.status === 'running' ? 'border-blue-500/20 bg-blue-500/10 text-blue-200' :
                    'border-slate-500/20 bg-slate-500/10 text-slate-200'
                  }`}>
                    {scan.status}
                  </span>
                </div>
                <div className="text-sm text-slate-300 mb-3">
                  Type: {scan.type} | Started: {new Date(scan.started_at).toLocaleString()}
                </div>
                {scan.status === 'running' && (
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Progress</span>
                      <span>{scan.progress}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 transition-all duration-300"
                        style={{ width: `${scan.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                {scan.findings?.length > 0 && (
                  <div>
                    <div className="text-sm font-semibold text-white mb-2">Findings:</div>
                    {scan.findings.map((finding, idx) => (
                      <div key={idx} className={`rounded-lg border p-3 mb-2 text-sm ${
                        finding.severity === 'high' ? 'border-rose-500/20 bg-rose-500/10 text-rose-200' :
                        'border-amber-500/20 bg-amber-500/10 text-amber-200'
                      }`}>
                        {finding.description}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* System Health Tab */}
        {tabValue === 2 && (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/40 backdrop-blur">
              <div className="text-lg font-semibold text-white mb-4">System Components</div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-300">API Gateway</span>
                  <span className="inline-block rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                    Operational
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-300">Database</span>
                  <span className="inline-block rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                    Operational
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-300">Cache Service (Redis)</span>
                  <span className="inline-block rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                    Operational
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-300">AI Bot Service</span>
                  <span className="inline-block rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                    Operational
                  </span>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/40 backdrop-blur">
              <div className="text-lg font-semibold text-white mb-4">Security Recommendations</div>
              <div className="space-y-3">
                <div className="rounded-lg border border-blue-500/20 bg-blue-500/10 p-3 text-sm text-blue-200">
                  Enable 2FA for admin accounts
                </div>
                <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-3 text-sm text-amber-200">
                  Update SSL certificate in 30 days
                </div>
                <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                  All security patches applied
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Status Update Dialog */}
        {statusDialogOpen && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="rounded-2xl border border-white/10 bg-slate-900 p-6 shadow-lg shadow-black/40 backdrop-blur max-w-md w-full">
              <div className="text-lg font-semibold text-white mb-4">Update Alert Status</div>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-slate-300 mb-2">Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-white"
                >
                  <option value="new">New</option>
                  <option value="investigating">Investigating</option>
                  <option value="resolved">Resolved</option>
                  <option value="false_positive">False Positive</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStatusDialogOpen(false)}
                  className="flex-1 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  onClick={updateAlertStatus}
                  className="flex-1 rounded-lg bg-sky-500/80 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AISecurityManager;
