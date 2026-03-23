import React, { useState } from 'react';
import strategyService from '../../../../services/strategyService';
import './StrategyAdvisor.css';

const timeframes = ['immediate', 'short_term', 'medium_term', 'long_term', 'all'];
const priorities = ['high', 'medium', 'low', 'all'];

const RecommendationsPanel = ({ pushNotification }) => {
    const [timeframe, setTimeframe] = useState('all');
    const [priority, setPriority] = useState('all');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);

    const [focusArea, setFocusArea] = useState('market_expansion');
    const [minRoi, setMinRoi] = useState('');
    const [generated, setGenerated] = useState(null);

    const loadRecommendations = async () => {
        setLoading(true);
        const result = await strategyService.getRecommendations({ timeframe, priority });
        setData(result.recommendations || {});
        setLoading(false);
        if (pushNotification) pushNotification('Recommendations loaded', 'success');
    };

    const generateCustom = async () => {
        setLoading(true);
        const constraints = {};
        if (minRoi) constraints.min_roi = Number(minRoi);
        const result = await strategyService.generateRecommendations({ focusArea, constraints });
        setGenerated(result);
        setLoading(false);
        if (pushNotification) pushNotification('Custom recommendations generated', 'info');
    };

    const renderGroup = (key, items) => (
        <div key={key} className="panel-sub">
            <div className="panel-sub-header">
                <h4>{key}</h4>
                <span className="pill ghost">{items.length} items</span>
            </div>
            <div className="list">
                {items.map((rec, idx) => (
                    <div key={idx} className="recommendation-card">
                        <div className="recommendation-title">{rec.action || rec.title}</div>
                        <div className="recommendation-meta">
                            <span className={`pill ${rec.priority || 'medium'}`}>{rec.priority || 'medium'}</span>
                            {rec.expected_roi && <span className="pill ghost">ROI {rec.expected_roi}</span>}
                            {rec.expected_impact && <span className="pill ghost">Impact {rec.expected_impact}</span>}
                        </div>
                        {rec.description && <div className="recommendation-desc">{rec.description}</div>}
                        {rec.timeline && <div className="recommendation-desc">Timeline: {rec.timeline}</div>}
                    </div>
                ))}
            </div>
        </div>
    );

    return (
        <div className="analysis-view">
            <div className="section-header">
                <div>
                    <p className="eyebrow">Strategic Actions</p>
                    <h2>Recommendations</h2>
                </div>
                <div className="row gap">
                    <select className="input" value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
                        {timeframes.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <select className="input" value={priority} onChange={(e) => setPriority(e.target.value)}>
                        {priorities.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <button className="primary" onClick={loadRecommendations} disabled={loading}>
                        {loading ? 'Loading...' : 'Load'}
                    </button>
                </div>
            </div>

            {data && Object.keys(data).length > 0 && (
                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <p className="eyebrow">Filtered</p>
                            <h3>Recommendations</h3>
                        </div>
                    </div>
                    {Object.entries(data).map(([key, items]) => renderGroup(key, items || []))}
                </div>
            )}

            <div className="panel">
                <div className="panel-header">
                    <div>
                        <p className="eyebrow">Generator</p>
                        <h3>Custom recommendations</h3>
                    </div>
                </div>
                <div className="row gap wrap">
                    <select className="input" value={focusArea} onChange={(e) => setFocusArea(e.target.value)}>
                        <option value="market_expansion">Market expansion</option>
                        <option value="operational_efficiency">Operational efficiency</option>
                        <option value="competitive">Competitive response</option>
                        <option value="financial_optimization">Financial optimization</option>
                    </select>
                    <input
                        className="input"
                        type="number"
                        value={minRoi}
                        onChange={(e) => setMinRoi(e.target.value)}
                        placeholder="Min ROI %"
                    />
                    <button className="secondary" onClick={generateCustom} disabled={loading}>
                        {loading ? 'Generating...' : 'Generate'}
                    </button>
                </div>

                {generated && (
                    <div className="panel-sub">
                        <h4>{generated.focus_area || 'Focus area'}</h4>
                        <div className="recommendation-desc">{generated.description}</div>
                        <ul className="bullet-list">
                            {(generated.recommendations || []).map((rec, idx) => (
                                <li key={idx}>
                                    <strong>{rec.title}:</strong> {rec.description} (Timeline: {rec.timeline || 'n/a'})
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RecommendationsPanel;
