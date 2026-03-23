import React from 'react';
import './StrategyAdvisor.css';

const MetricCard = ({ label, value, detail, trend }) => (
    <div className="metric-card">
        <div className="metric-label">{label}</div>
        <div className="metric-value">{value}</div>
        <div className="metric-detail">{detail}</div>
        {trend && <div className={`trend ${trend}`}>{trend === 'up' ? '' : trend === 'down' ? '' : ''}</div>}
    </div>
);

const StrategyDashboard = ({ data, loading, onRefresh }) => {
    const metrics = data?.key_metrics || {};
    const alerts = data?.strategic_alerts || [];
    const recommendations = data?.priority_recommendations || [];
    const watchlist = data?.competitor_watchlist || [];

    return (
        <div className="dashboard-view">
            <div className="section-header">
                <div>
                    <p className="eyebrow">Overview</p>
                    <h2>Strategic Dashboard</h2>
                </div>
                <button className="secondary" onClick={onRefresh} disabled={loading}>
                    {loading ? 'Refreshing...' : 'Refresh now'}
                </button>
            </div>

            <div className="metrics-grid">
                <MetricCard
                    label="Market Share"
                    value={metrics.market_position?.market_share || '--'}
                    detail={`Rank ${metrics.market_position?.rank || '-'} | Trend ${metrics.market_position?.trend || '-'}`}
                    trend={metrics.market_position?.trend}
                />
                <MetricCard
                    label="Revenue Growth"
                    value={metrics.financial_health?.revenue_growth || '--'}
                    detail={`Profit margin ${metrics.financial_health?.profit_margin || '--'} | ROI ${metrics.financial_health?.roi || '--'}`}
                    trend="up"
                />
                <MetricCard
                    label="Competitive Edge"
                    value={metrics.competitive_position?.competitive_advantage || '--'}
                    detail={`Differentiation ${metrics.competitive_position?.differentiation_score || '--'} | Loyalty ${metrics.competitive_position?.customer_loyalty || '--'}`}
                    trend="stable"
                />
            </div>

            <div className="grid two">
                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <p className="eyebrow">Strategic Alerts</p>
                            <h3>Immediate attention</h3>
                        </div>
                    </div>
                    {alerts.length === 0 && <div className="empty">No alerts right now.</div>}
                    <div className="list">
                        {alerts.map((alert, idx) => (
                            <div key={idx} className="alert-card">
                                <div className="alert-top">
                                    <span className={`pill ${alert.severity || 'medium'}`}>{alert.severity || 'medium'}</span>
                                    <span className="alert-type">{alert.type}</span>
                                </div>
                                <div className="alert-title">{alert.title}</div>
                                <div className="alert-desc">{alert.description}</div>
                                {alert.action && <div className="alert-action">Action: {alert.action}</div>}
                            </div>
                        ))}
                    </div>
                </div>

                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <p className="eyebrow">Priority Recommendations</p>
                            <h3>Top 3 actions</h3>
                        </div>
                    </div>
                    {recommendations.length === 0 && <div className="empty">No recommendations found.</div>}
                    <div className="list">
                        {recommendations.map((rec, idx) => (
                            <div key={idx} className="recommendation-card">
                                <div className="recommendation-title">{rec.action || rec.title}</div>
                                <div className="recommendation-meta">
                                    <span className={`pill ${rec.priority || 'medium'}`}>{rec.priority || 'medium'}</span>
                                    {rec.expected_impact && <span className="pill ghost">Impact: {rec.expected_impact}</span>}
                                </div>
                                {rec.estimated_effort && (
                                    <div className="recommendation-desc">Effort: {rec.estimated_effort}</div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="panel">
                <div className="panel-header">
                    <div>
                        <p className="eyebrow">Watchlist</p>
                        <h3>Competitors to monitor</h3>
                    </div>
                </div>
                {watchlist.length === 0 && <div className="empty">No competitors on watchlist.</div>}
                <div className="watchlist-grid">
                    {watchlist.map((item, idx) => (
                        <div key={idx} className="watch-card">
                            <div className="watch-name">{item.name || item.competitor || 'Unknown'}</div>
                            <div className="watch-detail">Threat: {item.threat_level || 'medium'}</div>
                            <div className="watch-detail">Recent actions: {(item.recent_actions || []).join(', ') || 'N/A'}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StrategyDashboard;
