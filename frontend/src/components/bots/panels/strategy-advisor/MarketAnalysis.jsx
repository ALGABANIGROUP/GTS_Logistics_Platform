import React, { useState } from 'react';
import strategyService from '../../../../services/strategyService';
import './StrategyAdvisor.css';

const MarketAnalysis = ({ pushNotification }) => {
    const [market, setMarket] = useState('uae');
    const [depth, setDepth] = useState('standard');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const runAnalysis = async () => {
        setLoading(true);
        const data = await strategyService.analyzeMarket({ marketName: market, depth });
        setResult(data);
        setLoading(false);
        if (pushNotification) pushNotification('Market analysis completed', 'success');
    };

    const runForecast = async () => {
        setLoading(true);
        const data = await strategyService.analyzeMarketEntry({ targetMarket: market });
        setResult((prev) => ({ ...(prev || {}), entry: data }));
        setLoading(false);
        if (pushNotification) pushNotification('Market entry scenario generated', 'info');
    };

    return (
        <div className="analysis-view">
            <div className="section-header">
                <div>
                    <p className="eyebrow">Market Intelligence</p>
                    <h2>Market analysis & entry</h2>
                </div>
                <div className="row gap">
                    <input
                        value={market}
                        onChange={(e) => setMarket(e.target.value)}
                        className="input"
                        placeholder="Enter market (e.g., uae, saudi_arabia)"
                    />
                    <select value={depth} onChange={(e) => setDepth(e.target.value)} className="input">
                        <option value="quick">Quick</option>
                        <option value="standard">Standard</option>
                        <option value="deep">Deep</option>
                    </select>
                    <button className="primary" onClick={runAnalysis} disabled={loading}>
                        {loading ? 'Analyzing...' : 'Run analysis'}
                    </button>
                    <button className="secondary" onClick={runForecast} disabled={loading}>
                        {loading ? 'Loading...' : 'Market entry'}
                    </button>
                </div>
            </div>

            {result && (
                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <p className="eyebrow">Results</p>
                            <h3>{result.market || result.analysis_type || 'Analysis'}</h3>
                        </div>
                    </div>
                    <div className="result-grid">
                        <div>
                            <h4>Overview</h4>
                            <pre className="json-view">{JSON.stringify(result.analysis || result, null, 2)}</pre>
                        </div>
                        {result.entry && (
                            <div>
                                <h4>Market entry scenario</h4>
                                <pre className="json-view">{JSON.stringify(result.entry, null, 2)}</pre>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MarketAnalysis;
