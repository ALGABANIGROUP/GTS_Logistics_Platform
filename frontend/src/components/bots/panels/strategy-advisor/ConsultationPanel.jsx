import React, { useState } from 'react';
import strategyService from '../../../../services/strategyService';
import './StrategyAdvisor.css';

const ConsultationPanel = ({ pushNotification }) => {
    const [question, setQuestion] = useState('What is the best strategy to expand into Saudi Arabia?');
    const [context, setContext] = useState('');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);

    const consult = async () => {
        if (!question) return;
        setLoading(true);
        const data = await strategyService.consult({ question, context });
        setResponse(data);
        setLoading(false);
        if (pushNotification) pushNotification('Consultation completed', 'success');
    };

    return (
        <div className="analysis-view">
            <div className="section-header">
                <div>
                    <p className="eyebrow">Decision Support</p>
                    <h2>Consult the advisor</h2>
                </div>
                <button className="primary" onClick={consult} disabled={loading}>
                    {loading ? 'Thinking...' : 'Run consultation'}
                </button>
            </div>

            <div className="panel">
                <div className="row gap wrap">
                    <input
                        className="input flex"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a strategic question"
                    />
                    <textarea
                        className="input flex"
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        placeholder="Optional context (JSON or free text)"
                        rows={3}
                    />
                </div>

                {response && (
                    <div className="panel-sub">
                        <div className="panel-sub-header">
                            <h4>Response</h4>
                            <span className="pill ghost">Confidence {Math.round((response.confidence || 0) * 100)}%</span>
                        </div>
                        <pre className="json-view">{JSON.stringify(response, null, 2)}</pre>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConsultationPanel;
