import React, { useState } from 'react';
import strategyService from '../../../../services/strategyService';
import './StrategyAdvisor.css';

const categories = [
    { value: 'all', label: 'All' },
    { value: 'global', label: 'Global' },
    { value: 'regional', label: 'Regional' },
    { value: 'digital', label: 'Digital' }
];

const CompetitorIntel = ({ pushNotification }) => {
    const [category, setCategory] = useState('all');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);

    const loadData = async () => {
        setLoading(true);
        const result = await strategyService.analyzeCompetitors(category);
        setData(result.analysis || result);
        setLoading(false);
        if (pushNotification) pushNotification('Competitor analysis updated', 'success');
    };

    return (
        <div className="analysis-view">
            <div className="section-header">
                <div>
                    <p className="eyebrow">Competitive Intelligence</p>
                    <h2>Competitor landscape</h2>
                </div>
                <div className="row gap">
                    <select value={category} onChange={(e) => setCategory(e.target.value)} className="input">
                        {categories.map((c) => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                        ))}
                    </select>
                    <button className="primary" onClick={loadData} disabled={loading}>
                        {loading ? 'Loading...' : 'Analyze'}
                    </button>
                </div>
            </div>

            {data && (
                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <p className="eyebrow">Results</p>
                            <h3>Competitive landscape</h3>
                        </div>
                    </div>

                    <div className="grid two">
                        <div className="panel-sub">
                            <p className="eyebrow">Landscape</p>
                            <div className="stat">Total competitors: {data.competitive_landscape?.total_competitors || 0}</div>
                            <div className="stat">Concentration: {data.competitive_landscape?.market_concentration || 'unknown'}</div>
                            <div className="stat">Intensity: {data.competitive_landscape?.competitive_intensity || 'unknown'}</div>
                        </div>

                        <div className="panel-sub">
                            <p className="eyebrow">Key Insights</p>
                            {(data.key_insights || []).length === 0 && <div className="empty">No insights available.</div>}
                            <ul className="bullet-list">
                                {(data.key_insights || []).map((i, idx) => (
                                    <li key={idx}>{i.insight || i}</li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="panel-sub">
                        <p className="eyebrow">Threat assessment</p>
                        {(data.threat_assessment || []).length === 0 && <div className="empty">No threats detected.</div>}
                        <div className="list">
                            {(data.threat_assessment || []).map((item, idx) => (
                                <div key={idx} className="alert-card">
                                    <div className="alert-top">
                                        <span className={`pill ${item.threat_level || 'medium'}`}>{item.threat_level || 'medium'}</span>
                                        <span className="alert-type">{item.competitor}</span>
                                    </div>
                                    <div className="alert-title">{item.category}</div>
                                    <div className="alert-desc">Primary threats: {(item.primary_threats || []).join(', ')}</div>
                                    <div className="alert-action">Monitoring: {(item.recommended_monitoring || []).join(', ') || 'N/A'}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="panel-sub">
                        <p className="eyebrow">Opportunities</p>
                        {(data.opportunity_analysis || []).length === 0 && <div className="empty">No opportunities detected.</div>}
                        <div className="list">
                            {(data.opportunity_analysis || []).map((op, idx) => (
                                <div key={idx} className="recommendation-card">
                                    <div className="recommendation-title">{op.competitor}</div>
                                    <div className="recommendation-meta">
                                        <span className="pill ghost">Impact: {op.potential_impact || 'medium'}</span>
                                    </div>
                                    <div className="recommendation-desc">{op.exploitation_strategy}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompetitorIntel;
