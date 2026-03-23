// GeneralManagerControl.jsx
import React, { useState } from 'react';

const GeneralManagerControl = () => {
  const [activeTab, setActiveTab] = useState('executive_dashboard');
  const [botStatus, setBotStatus] = useState({
    status: 'INACTIVE',
    timestamp: 'Never',
    last_execution: 'Never'
  });

  const [reportConfig, setReportConfig] = useState({
    import_sources: ['portal'],
    date_range: { start: '', end: '' },
    report_type: 'strategic_overview',
    include_analytics: false
  });

  const [message, setMessage] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [newSource, setNewSource] = useState('');
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configDraft, setConfigDraft] = useState('');

  const tabs = [
    { id: 'executive_dashboard', name: 'Executive Dashboard', icon: '' },
    { id: 'report_generator', name: 'Report Generator', icon: '' },
    { id: 'execution_control', name: 'Execution Control', icon: '' },
    { id: 'monitoring', name: 'Monitoring', icon: '' }
  ];

  const handleRunBot = (type = 'basic') => {
    console.log(`Running General Manager Bot - ${type}`);
    setBotStatus({
      status: 'RUNNING',
      timestamp: new Date().toLocaleTimeString(),
      last_execution: 'Now'
    });

    // Simulate execution
    setTimeout(() => {
      setBotStatus({
        status: 'COMPLETED',
        timestamp: new Date().toLocaleTimeString(),
        last_execution: 'Just now'
      });
    }, 2000);
  };

  const handleRefresh = () => {
    console.log('Refreshing status...');
    // Refresh logic here
  };

  const handleGenerateReport = () => {
    console.log('Generating report with config:', reportConfig);
    setFeedback({ type: 'success', message: 'Report generation started.' });
  };

  const openAddSourceModal = () => {
    setNewSource('');
    setShowSourceModal(true);
  };

  const submitNewSource = () => {
    const value = newSource.trim();
    if (!value) {
      setFeedback({ type: 'error', message: 'Enter a data source name first.' });
      return;
    }
    setReportConfig({
      ...reportConfig,
      import_sources: [...reportConfig.import_sources, value]
    });
    setShowSourceModal(false);
    setFeedback({ type: 'success', message: `Source "${value}" added.` });
  };

  const openConfigModal = () => {
    setConfigDraft(JSON.stringify(reportConfig, null, 2));
    setShowConfigModal(true);
  };

  const submitConfigDraft = () => {
    try {
      setReportConfig(JSON.parse(configDraft));
      setShowConfigModal(false);
      setFeedback({ type: 'success', message: 'Configuration updated.' });
    } catch (e) {
      setFeedback({ type: 'error', message: 'Invalid JSON.' });
    }
  };

  return (
    <div className="general-manager-control">
      {/* Header */}
      <header className="gm-header">
        <div className="gm-title">
          <h1>GENERAL MANAGER CONTROL</h1>
          <p>Executive Oversight & Strategic Reporting</p>
        </div>

        <div className="gm-stats">
          <div className="stat">
            <div className="stat-value">0</div>
            <div className="stat-label">Active Reports</div>
          </div>
          <div className="stat">
            <div className="stat-value">0</div>
            <div className="stat-label">Alerts</div>
          </div>
        </div>

        <div className="gm-actions">
            <button className="btn-primary" onClick={() => handleRunBot('advanced')}>
              Generate Report
            </button>
            <button className="btn-secondary" onClick={() => handleRunBot('strategic')}>
              Analyze
            </button>
            <button className="btn-secondary" onClick={() => handleRunBot('emergency')}>
              Strategic Review
            </button>
            <button className="btn-danger" onClick={() => handleRunBot('emergency')}>
              Emergency Brief
            </button>
        </div>
      </header>

      {feedback && (
        <div
          style={{
            marginBottom: "16px",
            padding: "12px 14px",
            borderRadius: "10px",
            border: feedback.type === "success" ? "1px solid rgba(52, 211, 153, 0.35)" : "1px solid rgba(248, 113, 113, 0.35)",
            background: feedback.type === "success" ? "rgba(52, 211, 153, 0.12)" : "rgba(248, 113, 113, 0.12)",
            color: "#ffffff",
            display: "flex",
            justifyContent: "space-between",
            gap: "12px",
            alignItems: "center",
          }}
        >
          <span>{feedback.message}</span>
          <button
            type="button"
            className="btn-outline"
            onClick={() => setFeedback(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <nav className="gm-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`gm-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main className="gm-content">
        {activeTab === 'executive_dashboard' && (
          <div className="tab-panel">
            <div className="section">
              <h2>Strategic Overview</h2>
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-name">Company Performance</div>
                  <div className="kpi-value">0%</div>
                  <div className="kpi-target">Target: 100%</div>
                  <div className="kpi-status">?</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-name">Market Position</div>
                  <div className="kpi-value">0</div>
                  <div className="kpi-target">Target: 10</div>
                  <div className="kpi-status">?</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-name">Revenue Growth</div>
                  <div className="kpi-value">$0</div>
                  <div className="kpi-target">Target: $2.5M</div>
                  <div className="kpi-status">?</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-name">Team Efficiency</div>
                  <div className="kpi-value">0%</div>
                  <div className="kpi-target">Target: 95%</div>
                  <div className="kpi-status">?</div>
                </div>
              </div>
              <div className="last-updated">Last updated: Never</div>
            </div>

            <div className="section">
              <h2>Business Health</h2>
              <div className="health-grid">
                <div className="health-item">
                  <div className="health-area">Operations</div>
                  <div className="health-status">Not Monitored</div>
                  <div className="health-trend">-</div>
                </div>
                <div className="health-item">
                  <div className="health-area">Finance</div>
                  <div className="health-status">Not Monitored</div>
                  <div className="health-trend">-</div>
                </div>
                <div className="health-item">
                  <div className="health-area">Sales</div>
                  <div className="health-status">Not Monitored</div>
                  <div className="health-trend">-</div>
                </div>
                <div className="health-item">
                  <div className="health-area">Customer Satisfaction</div>
                  <div className="health-status">Not Monitored</div>
                  <div className="health-trend">-</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'report_generator' && (
          <div className="tab-panel">
            <div className="section">
              <h2>Report Configuration</h2>
              <div className="config-form">
                <div className="form-group">
                  <label>Import Sources:</label>
                  <div className="sources-list">
                    {reportConfig.import_sources.map((source, idx) => (
                      <div key={idx} className="source-tag">
                        {source}
                        <button className="remove-btn">x</button>
                      </div>
                    ))}
                    <button className="add-btn" onClick={openAddSourceModal}>
                      + Add Source
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <label>Date Range:</label>
                  <div className="date-inputs">
                    <input
                      type="date"
                      value={reportConfig.date_range.start}
                      onChange={(e) => setReportConfig({
                        ...reportConfig,
                        date_range: { ...reportConfig.date_range, start: e.target.value }
                      })}
                      placeholder="Start Date"
                    />
                    <span>to</span>
                    <input
                      type="date"
                      value={reportConfig.date_range.end}
                      onChange={(e) => setReportConfig({
                        ...reportConfig,
                        date_range: { ...reportConfig.date_range, end: e.target.value }
                      })}
                      placeholder="End Date"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Report Type:</label>
                  <select
                    value={reportConfig.report_type}
                    onChange={(e) => setReportConfig({ ...reportConfig, report_type: e.target.value })}
                  >
                    <option value="strategic_overview">Strategic Overview</option>
                    <option value="performance_review">Performance Review</option>
                    <option value="financial_analysis">Financial Analysis</option>
                    <option value="operational_report">Operational Report</option>
                  </select>
                </div>

                <div className="form-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={reportConfig.include_analytics}
                      onChange={(e) => setReportConfig({
                        ...reportConfig,
                        include_analytics: e.target.checked
                      })}
                    />
                    Include Advanced Analytics
                  </label>
                </div>

                <div className="form-actions">
                  <button className="btn-primary" onClick={handleGenerateReport}>
                     Generate Report
                  </button>
                  <button className="btn-secondary">
                     Save Template
                  </button>
                </div>
              </div>
            </div>

            <div className="section">
              <h2>Report Templates</h2>
              <div className="templates-list">
                <div className="template-card">
                  <div className="template-name">Weekly Executive Summary</div>
                  <div className="template-status">Not Configured</div>
                  <button className="template-btn">Configure</button>
                </div>
                <div className="template-card">
                  <div className="template-name">Monthly Performance Review</div>
                  <div className="template-status">Not Configured</div>
                  <button className="template-btn">Configure</button>
                </div>
                <div className="template-card">
                  <div className="template-name">Quarterly Strategic Report</div>
                  <div className="template-status">Not Configured</div>
                  <button className="template-btn">Configure</button>
                </div>
                <div className="template-card">
                  <div className="template-name">Annual Business Review</div>
                  <div className="template-status">Not Configured</div>
                  <button className="template-btn">Configure</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'execution_control' && (
          <div className="tab-panel">
            <div className="section">
              <h2>Bot Execution</h2>

              <div className="status-display">
                <div className="status-info">
                  <div className="status-item">
                    <span className="status-label">Status:</span>
                    <span className={`status-value ${botStatus.status.toLowerCase()}`}>
                      {botStatus.status === 'RUNNING' ? ' RUNNING' :
                        botStatus.status === 'COMPLETED' ? ' COMPLETED' : ' INACTIVE'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Timestamp:</span>
                    <span className="status-value">{botStatus.timestamp}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Last Execution:</span>
                    <span className="status-value">{botStatus.last_execution}</span>
                  </div>
                </div>

                <div className="status-actions">
                  <button className="btn-primary" onClick={() => handleRunBot('basic')}>
                     Run Basic Report
                  </button>
                  <button className="btn-secondary" onClick={() => handleRunBot('advanced')}>
                     Run with Parameters
                  </button>
                  <button className="btn-danger" onClick={() => handleRunBot('emergency')}>
                     Emergency Briefing
                  </button>
                  <button className="btn-outline" onClick={handleRefresh}>
                     Refresh Status
                  </button>
                </div>
              </div>
            </div>

            <div className="section">
              <h2>Message to Bot</h2>
              <div className="message-input">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter strategic instructions for the General Manager bot..."
                  rows={6}
                />
                <div className="message-examples">
                  <p>Examples:</p>
                  <ul>
                    <li>Analyze Q3 performance vs competitors</li>
                    <li>Generate growth strategy for next quarter</li>
                    <li>Review operational efficiency across departments</li>
                  </ul>
                </div>

                <div className="message-actions">
                  <button
                    className="btn-primary"
                    onClick={() => {
                      if (message.trim()) {
                        console.log('Sending message to bot:', message);
                        handleRunBot('custom');
                      }
                    }}
                    disabled={!message.trim()}
                  >
                     Send to Bot
                  </button>
                  <button className="btn-outline" onClick={() => setMessage('')}>
                     Clear
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="tab-panel">
            <div className="section">
              <h2>Status & Logs</h2>
              <div className="monitoring-grid">
                <div className="monitor-card">
                  <h3>Current Status</h3>
                  <div className="monitor-details">
                    <div className="detail">
                      <span className="label">Bot Status:</span>
                      <span className="value">{botStatus.status}</span>
                    </div>
                    <div className="detail">
                      <span className="label">Last Check:</span>
                      <span className="value">{botStatus.timestamp}</span>
                    </div>
                    <div className="detail">
                      <span className="label">Uptime:</span>
                      <span className="value">0%</span>
                    </div>
                  </div>
                </div>

                <div className="monitor-card">
                  <h3>Recent Activity</h3>
                  <div className="activity-list">
                    <div className="empty-activity">
                      No recent activity
                    </div>
                  </div>
                </div>

                <div className="monitor-card">
                  <h3>Error Logs</h3>
                  <div className="error-list">
                    <div className="empty-error">
                      No errors reported
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="section">
              <h2>Configuration</h2>
              <div className="config-view">
                <pre className="config-code">
                  {`{
  "import": [
    "portal",
    "start_date": "${reportConfig.date_range.start}",
    "end_date": "${reportConfig.date_range.end}",
    "round": 1,
    "include_iris": ${reportConfig.include_analytics}
  ]
}`}
                </pre>

                <div className="config-actions">
                  <button className="btn-primary" onClick={openConfigModal}>
                     Edit Config
                  </button>
                  <button className="btn-secondary">
                     Save Changes
                  </button>
                  <button className="btn-outline" onClick={handleRefresh}>
                     Reset to Defaults
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Side Panel */}
      <aside className="gm-sidebar">
        <div className="sidebar-section">
          <h3>Executive Tools</h3>
          <div className="tools-list">
            <button className="tool-btn">
              <span className="tool-icon"></span>
              <div className="tool-info">
                <div className="tool-name">Generate Standard Report</div>
                <div className="tool-desc">Weekly performance review</div>
              </div>
            </button>

            <button className="tool-btn">
              <span className="tool-icon"></span>
              <div className="tool-info">
                <div className="tool-name">Strategic Analysis</div>
                <div className="tool-desc">Market & competitor analysis</div>
              </div>
            </button>

            <button className="tool-btn">
              <span className="tool-icon"></span>
              <div className="tool-info">
                <div className="tool-name">Performance Dashboard</div>
                <div className="tool-desc">Live business metrics</div>
              </div>
            </button>

            <button className="tool-btn">
              <span className="tool-icon"></span>
              <div className="tool-info">
                <div className="tool-name">Crisis Management</div>
                <div className="tool-desc">Emergency response planning</div>
              </div>
            </button>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>Related Tools</h3>
          <div className="related-tools">
            <button className="related-btn">
              <span className="related-icon"></span>
              Reports
            </button>
            <button className="related-btn">
              <span className="related-icon"></span>
              Analytics
            </button>
            <button className="related-btn">
              <span className="related-icon"></span>
              Forecasting
            </button>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>System Status</h3>
          <div className="system-status">
            <div className="status-item">
              <span className="status-label">Data Sources:</span>
              <span className="status-value">0 connected</span>
            </div>
            <div className="status-item">
              <span className="status-label">Report Templates:</span>
              <span className="status-value">4 available</span>
            </div>
            <div className="status-item">
              <span className="status-label">Automation:</span>
              <span className="status-value"> Inactive</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Footer */}
      <footer className="gm-footer">
        <div className="footer-left">
          <span className="bot-name">General Manager Bot</span>
          <span className={`bot-status ${botStatus.status.toLowerCase()}`}>
            {botStatus.status === 'RUNNING' ? ' Running' :
              botStatus.status === 'COMPLETED' ? ' Active' : ' Inactive'}
          </span>
        </div>

        <div className="footer-right">
          <button className="footer-btn" onClick={handleRefresh}>
             Refresh Status
          </button>
          <button className="footer-btn" onClick={() => handleRunBot('basic')}>
             Run Bot
          </button>
          <button className="footer-btn">
             Configure
          </button>
        </div>
      </footer>

      {showSourceModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(2, 6, 23, 0.72)", display: "flex", alignItems: "center", justifyContent: "center", padding: "16px", zIndex: 50 }}>
          <div style={{ width: "min(420px, 100%)", background: "#0f172a", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "16px", padding: "22px", boxShadow: "0 20px 50px rgba(0,0,0,0.4)" }}>
            <h3 style={{ margin: "0 0 8px 0", color: "#fff" }}>Add Data Source</h3>
            <p style={{ margin: "0 0 14px 0", color: "#cbd5e1" }}>Add a new report import source.</p>
            <input
              type="text"
              value={newSource}
              onChange={(e) => setNewSource(e.target.value)}
              placeholder="e.g. finance"
              style={{ width: "100%", padding: "10px 12px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.04)", color: "#fff" }}
            />
            <div style={{ marginTop: "16px", display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button className="btn-outline" onClick={() => setShowSourceModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={submitNewSource}>Add Source</button>
            </div>
          </div>
        </div>
      )}

      {showConfigModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(2, 6, 23, 0.72)", display: "flex", alignItems: "center", justifyContent: "center", padding: "16px", zIndex: 50 }}>
          <div style={{ width: "min(720px, 100%)", background: "#0f172a", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "16px", padding: "22px", boxShadow: "0 20px 50px rgba(0,0,0,0.4)" }}>
            <h3 style={{ margin: "0 0 8px 0", color: "#fff" }}>Edit JSON Configuration</h3>
            <p style={{ margin: "0 0 14px 0", color: "#cbd5e1" }}>Update the report configuration without leaving the page.</p>
            <textarea
              value={configDraft}
              onChange={(e) => setConfigDraft(e.target.value)}
              rows={14}
              style={{ width: "100%", padding: "12px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.04)", color: "#fff", fontFamily: "monospace" }}
            />
            <div style={{ marginTop: "16px", display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button className="btn-outline" onClick={() => setShowConfigModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={submitConfigDraft}>Save Config</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeneralManagerControl;
