/**
 * MapleLoad Canada Bot Control Panel
 * Unified Canadian Logistics Intelligence & Freight Sourcing Platform
 * v2.0.0
 */

import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import './MapleLoadCanadaControl.css';

const MapleLoadCanadaControl = () => {
  const [activeTab, setActiveTab] = useState('intelligence');
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('hybrid');
  const [optimizationGoal, setOptimizationGoal] = useState('balanced');

  const botEndpoint = '/api/v1/ai/bots/mapleload-canada';

  // Fetch bot status on mount
  useEffect(() => {
    fetchBotStatus();
  }, []);

  const fetchBotStatus = async () => {
    try {
      const response = await axiosClient.get(`${botEndpoint}/status`);
      setBotStatus(response.data.data || response.data);
    } catch (error) {
      console.error('Failed to fetch bot status:', error);
    }
  };

  const executeBotFunction = async (endpoint, data = {}) => {
    setIsExecuting(true);
    try {
      const response = await axiosClient.post(`${botEndpoint}${endpoint}`, data);
      const result = response.data;
      setLastResult({
        endpoint,
        timestamp: new Date().toISOString(),
        success: result.ok || result.success,
        data: result.data || result,
        execution_id: result.execution_id
      });
    } catch (error) {
      setLastResult({
        endpoint,
        timestamp: new Date().toISOString(),
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const tabs = [
    { id: 'intelligence', name: ' Market Intelligence', icon: '' },
    { id: 'carriers', name: ' Carrier Discovery', icon: '' },
    { id: 'sourcing', name: ' Freight Sourcing', icon: '' },
    { id: 'matching', name: ' Smart Matching', icon: '' },
    { id: 'predictive', name: ' Predictive Analytics', icon: '' },
    { id: 'outreach', name: ' Outreach Automation', icon: '' },
    { id: 'leads', name: ' Lead Generation', icon: '' },
    { id: 'reports', name: ' Advanced Reports', icon: '' },
    { id: 'integrations', name: ' Integrations', icon: '' }
  ];

  return (
    <div className="mapleload-canada-control">
      {/* Header */}
      <div className="control-header mapleload-unified">
        <div className="header-main">
          <div className="header-title">
            <span className="header-icon">
              <img
                src="/canada-maple-leaf.svg"
                alt="Canada Maple Leaf"
                style={{ width: '50px', height: '50px' }}
              />
            </span>
            <div>
              <h1>MapleLoad Canada</h1>
              <p className="bot-description">
                Integrated Canadian Logistics Intelligence & Freight Sourcing Platform
              </p>
              <div className="version-badge">v2.0.0 - Unified Intelligence & Sourcing</div>
            </div>
          </div>

          {botStatus && (
            <div className="header-stats">
              <div className="stat-box">
                <div className="stat-value">-</div>
                <div className="stat-label">Carriers</div>
              </div>
              <div className="stat-box">
                <div className="stat-value">-</div>
                <div className="stat-label">Loads</div>
              </div>
              <div className="stat-box">
                <div className="stat-value">-</div>
                <div className="stat-label">Coverage</div>
              </div>
              <div className="stat-box">
                <div className="stat-value">-</div>
                <div className="stat-label">Success</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="control-tabs unified">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            title={tab.name}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.name}</span>
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main className="control-content">
        {/* Market Intelligence */}
        {activeTab === 'intelligence' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Canadian Market Intelligence</h2>
              <p>Real-time market analysis and strategic insights for Canadian freight market</p>
            </div>

            <button
              className="execute-btn orange"
              onClick={() => executeBotFunction('/admin/market-intelligence')}
              disabled={isExecuting}
            >
              {isExecuting ? ' Analyzing...' : ' Run Market Analysis'}
            </button>
          </div>
        )}

        {/* Carrier Discovery */}
        {activeTab === 'carriers' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Canadian Carrier Discovery</h2>
              <p>Find and evaluate carriers across Canada with AI-powered ranking</p>
            </div>

            <button
              className="execute-btn blue"
              onClick={() => executeBotFunction('/carrier-discovery')}
              disabled={isExecuting}
            >
              {isExecuting ? ' Searching...' : ' Discover New Carriers'}
            </button>
          </div>
        )}

        {/* Freight Sourcing */}
        {activeTab === 'sourcing' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Freight Sourcing & Matching</h2>
              <p>Find available loads and match with optimal carriers</p>
            </div>

            <button
              className="execute-btn green"
              onClick={() => executeBotFunction('/freight-sourcing')}
              disabled={isExecuting}
            >
              {isExecuting ? ' Sourcing...' : ' Find Available Loads'}
            </button>
          </div>
        )}

        {/* Smart Matching */}
        {activeTab === 'matching' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> AI-Powered Smart Matching</h2>
              <p>Intelligent load-carrier matching with neural network algorithm</p>
            </div>

            <div className="matching-controls">
              <div className="control-group">
                <label>Matching Algorithm:</label>
                <select
                  value={selectedAlgorithm}
                  onChange={(e) => setSelectedAlgorithm(e.target.value)}
                >
                  <option value="neural_network">Neural Network (94%)</option>
                  <option value="random_forest">Random Forest (92%)</option>
                  <option value="gradient_boosting">Gradient Boosting (91%)</option>
                  <option value="hybrid">Hybrid AI (95%)</option>
                </select>
              </div>

              <div className="control-group">
                <label>Optimization Goal:</label>
                <select
                  value={optimizationGoal}
                  onChange={(e) => setOptimizationGoal(e.target.value)}
                >
                  <option value="profit"> Maximize Profit</option>
                  <option value="speed"> Minimize Time</option>
                  <option value="reliability"> Maximize Reliability</option>
                  <option value="balanced"> Balanced Approach</option>
                </select>
              </div>
            </div>

            <button
              className="execute-btn blue"
              onClick={() =>
                executeBotFunction('/smart-matching', {
                  algorithm: selectedAlgorithm,
                  optimization_goal: optimizationGoal
                })
              }
              disabled={isExecuting}
            >
              {isExecuting ? ' Matching...' : ' Run Smart Matching'}
            </button>
          </div>
        )}

        {/* Predictive Analytics */}
        {activeTab === 'predictive' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Predictive Analytics</h2>
              <p>AI-powered forecasting and market trend predictions</p>
            </div>

            <div className="prediction-controls">
              <div className="prediction-card">
                <h3> Demand Forecasting</h3>
                <p>Predict shipment volumes and peak demand periods</p>
              </div>
              <div className="prediction-card">
                <h3> Pricing Trends</h3>
                <p>Forecast rate fluctuations and optimal pricing windows</p>
              </div>
              <div className="prediction-card">
                <h3> Capacity Planning</h3>
                <p>Predict carrier availability and market capacity</p>
              </div>
            </div>

            <button
              className="execute-btn purple"
              onClick={() =>
                executeBotFunction('/predictive-analytics', {
                  forecast_type: 'demand',
                  confidence_level: 85
                })
              }
              disabled={isExecuting}
            >
              {isExecuting ? ' Forecasting...' : ' Generate Predictions'}
            </button>
          </div>
        )}

        {/* Outreach Automation */}
        {activeTab === 'outreach' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Outreach & Communication Automation</h2>
              <p>Automated email campaigns and carrier engagement</p>
            </div>

            <div className="outreach-controls">
              <button className="campaign-btn orange"> Create Campaign</button>
              <button className="campaign-btn blue"> Analyze Responses</button>
              <button className="campaign-btn green"> Schedule Follow-ups</button>
              <button
                className="campaign-btn purple"
                onClick={() => executeBotFunction('/outreach-campaign', {
                  name: 'High Margin Loads Campaign',
                  target: 'all_carriers'
                })}
                disabled={isExecuting}
              >
                Launch Campaign
              </button>
            </div>
          </div>
        )}

        {/* Lead Generation */}
        {activeTab === 'leads' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Lead Generation & Qualification</h2>
              <p>Identify and qualify potential customers with AI scoring</p>
            </div>

            <div className="lead-stats">
              <div className="lead-metric">
                <div className="metric-value">1,247</div>
                <div className="metric-label">New Leads This Month</div>
              </div>
              <div className="lead-metric">
                <div className="metric-value">23%</div>
                <div className="metric-label">Conversion Rate</div>
              </div>
              <div className="lead-metric">
                <div className="metric-value">$2.4M</div>
                <div className="metric-label">Potential Revenue</div>
              </div>
            </div>

            <button
              className="execute-btn green"
              onClick={() =>
                executeBotFunction('/lead-generation', {
                  industry: 'manufacturing',
                  region: 'all'
                })
              }
              disabled={isExecuting}
            >
              {isExecuting ? ' Generating...' : ' Generate Leads'}
            </button>
          </div>
        )}

        {/* Advanced Reports */}
        {activeTab === 'reports' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> Advanced Reporting Suite</h2>
              <p>Comprehensive analytics and insights reporting</p>
            </div>

            <div className="report-types">
              <div className="report-type-card">
                <div className="report-icon"></div>
                <div className="report-name">Performance Analytics</div>
                <button
                  onClick={() =>
                    executeBotFunction('/advanced-report', {
                      report_type: 'performance',
                      output_format: 'json'
                    })
                  }
                >
                  Generate
                </button>
              </div>

              <div className="report-type-card">
                <div className="report-icon"></div>
                <div className="report-name">Financial Insights</div>
                <button
                  onClick={() =>
                    executeBotFunction('/advanced-report', {
                      report_type: 'financial',
                      output_format: 'json'
                    })
                  }
                >
                  Generate
                </button>
              </div>

              <div className="report-type-card">
                <div className="report-icon"></div>
                <div className="report-name">Market Intelligence</div>
                <button
                  onClick={() =>
                    executeBotFunction('/advanced-report', {
                      report_type: 'market',
                      output_format: 'json'
                    })
                  }
                >
                  Generate
                </button>
              </div>

              <div className="report-type-card">
                <div className="report-icon"></div>
                <div className="report-name">Carrier Performance</div>
                <button
                  onClick={() =>
                    executeBotFunction('/advanced-report', {
                      report_type: 'carrier',
                      output_format: 'json'
                    })
                  }
                >
                  Generate
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Integrations */}
        {activeTab === 'integrations' && (
          <div className="tab-content">
            <div className="content-header">
              <h2> API & Integrations Hub</h2>
              <p>Connect with external systems and automate workflows</p>
            </div>

            <div className="integrations-grid">
              <div className="integration-card disconnected">
                <div className="integration-header">
                  <span className="integration-icon"></span>
                  <span>Salesforce CRM</span>
                  <span className="status-badge"> Not Connected</span>
                </div>
                <div className="integration-details">
                  Setup required: API credentials
                </div>
              </div>

              <div className="integration-card disconnected">
                <div className="integration-header">
                  <span className="integration-icon"></span>
                  <span>QuickBooks</span>
                  <span className="status-badge"> Not Connected</span>
                </div>
                <div className="integration-details">
                  Setup required: OAuth token
                </div>
              </div>

              <div className="integration-card disconnected">
                <div className="integration-header">
                  <span className="integration-icon"></span>
                  <span>Google Sheets</span>
                  <span className="status-badge"> Not Connected</span>
                </div>
                <div className="integration-details">
                  Setup required: Sheet ID & API key
                </div>
              </div>

              <div className="integration-card disconnected">
                <div className="integration-header">
                  <span className="integration-icon"></span>
                  <span>Slack</span>
                  <span className="status-badge"> Not Connected</span>
                </div>
                <div className="integration-details">
                  Setup required: Webhook URL
                </div>
              </div>
            </div>

            <button
              className="execute-btn blue"
              onClick={() => executeBotFunction('/integrations')}
              disabled={isExecuting}
            >
              {isExecuting ? ' Checking...' : ' Check Integration Status'}
            </button>
          </div>
        )}
      </main>

      {/* Results Panel */}
      {lastResult && (
        <div className="results-panel unified">
          <div className="results-header">
            <h3> Execution Results</h3>
            <button className="close-btn" onClick={() => setLastResult(null)}></button>
          </div>
          <div className="results-content">
            <div className="result-status">
              {lastResult.success ? ' Success' : ' Error'}
              {lastResult.execution_id && ` (ID: ${lastResult.execution_id})`}
            </div>
            {lastResult.success && lastResult.data ? (
              <div className="result-grid">
                {lastResult.data.market_overview && (
                  <section className="result-section">
                    <h4>Market Overview</h4>
                    <div className="overview-cards">
                      <div className="mini-card"> Active carriers: <strong>{lastResult.data.market_overview.active_carriers}</strong></div>
                      <div className="mini-card"> Loads available: <strong>{lastResult.data.market_overview.loads_available}</strong> ({lastResult.data.market_overview.load_growth})</div>
                      <div className="mini-card"> Carrier growth: <strong>{lastResult.data.market_overview.carrier_growth}</strong></div>
                      <div className="mini-card"> Coverage: <strong>{lastResult.data.market_overview.market_coverage}</strong></div>
                    </div>
                  </section>
                )}

                {lastResult.data.provincial_breakdown && (
                  <section className="result-section">
                    <h4>Provincial Breakdown</h4>
                    <div className="table-like">
                      <div className="table-head">
                        <span>Province</span><span>Loads</span><span>Avg Rate</span><span>Capacity</span><span>Trend</span>
                      </div>
                      {Object.entries(lastResult.data.provincial_breakdown).map(([province, stats]) => (
                        <div key={province} className="table-row">
                          <span className="caps">{province.replace('_', ' ')}</span>
                          <span>{stats.loads}</span>
                          <span>{stats.avg_rate}</span>
                          <span>{stats.capacity}</span>
                          <span className={`trend ${stats.trend}`}>{stats.trend}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {lastResult.data.top_routes && Array.isArray(lastResult.data.top_routes) && (
                  <section className="result-section">
                    <h4>Top Routes</h4>
                    <div className="routes-grid">
                      {lastResult.data.top_routes.map((route, idx) => (
                        <div key={idx} className="route-card">
                          <div className="route-name">{route.route}</div>
                          <div className="route-meta">Volume: {route.volume}</div>
                          <div className="route-meta">Rate: {route.rate}</div>
                          <div className={`route-trend ${route.trend}`}>{route.trend}</div>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {lastResult.data.strategic_insights && Array.isArray(lastResult.data.strategic_insights) && (
                  <section className="result-section">
                    <h4>Strategic Insights</h4>
                    <ul className="insights-list">
                      {lastResult.data.strategic_insights.map((item, idx) => (
                        <li key={idx}>
                          <div className="insight-title">{item.insight}</div>
                          <div className="insight-text">{item.content}</div>
                        </li>
                      ))}
                    </ul>
                  </section>
                )}

                {lastResult.data.timestamp && (
                  <div className="timestamp">Last updated: {new Date(lastResult.data.timestamp).toLocaleString()}</div>
                )}
              </div>
            ) : (
              <pre>{JSON.stringify(lastResult.data || lastResult.error, null, 2)}</pre>
            )}
          </div>
        </div>
      )}

      {/* Status Bar */}
      <footer className="control-footer">
        <div className="footer-info">
          <span className="status-indicator active"> System Active</span>
          <span className="last-update">Last updated: Just now</span>
        </div>
        <div className="footer-actions">
          <button className="footer-btn" onClick={fetchBotStatus}> Refresh</button>
          <button className="footer-btn"> Settings</button>
          <button className="footer-btn"> Export Data</button>
        </div>
      </footer>
    </div>
  );
};

export default MapleLoadCanadaControl;
