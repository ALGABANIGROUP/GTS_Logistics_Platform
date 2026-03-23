// frontend/src/components/analytics/PerformanceAnalyticsDashboard.jsx
import React, { useState, useEffect } from 'react';

const PerformanceAnalyticsDashboard = () => {
    const [selectedBot, setSelectedBot] = useState('all');
    const [performanceData, setPerformanceData] = useState({});
    const [predictions, setPredictions] = useState({});

    useEffect(() => {
        loadPerformanceData();
    }, [selectedBot]);

    const loadPerformanceData = async () => {
        const data = await window.analyticsEngine.getPerformanceReport(selectedBot);
        setPerformanceData(data);

        const preds = await window.analyticsEngine.getPredictions(selectedBot);
        setPredictions(preds);
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">📊 Advanced Performance Analytics</h2>
                <select
                    value={selectedBot}
                    onChange={(e) => setSelectedBot(e.target.value)}
                    className="border rounded-lg px-3 py-2"
                >
                    <option value="all">All Bots</option>
                    <option value="freight_broker">Freight Broker</option>
                    <option value="documents_manager">Documents Manager</option>
                    <option value="general_manager">General Manager</option>
                </select>
            </div>

            <div className="grid grid-cols-3 gap-6">
                {/* Overall Performance Card */}
                <div className="col-span-2 bg-white p-6 rounded-xl shadow-lg">
                    <h4 className="font-semibold mb-4">📈 Key Performance Indicators</h4>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 border rounded-lg">
                            <div className="text-2xl font-bold text-green-600">
                                {performanceData.accuracy || '95%'}
                            </div>
                            <div className="text-sm text-gray-600">Accuracy</div>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">
                                {performanceData.responseTime || '150ms'}
                            </div>
                            <div className="text-sm text-gray-600">Response Time</div>
                        </div>
                    </div>
                </div>

                {/* Predictions */}
                <div className="bg-white p-6 rounded-xl shadow-lg">
                    <h4 className="font-semibold mb-4">🔮 Predictions</h4>
                    {predictions.trend && (
                        <div className={`p-3 rounded-lg ${predictions.trend === 'improving' ? 'bg-green-100' :
                                predictions.trend === 'declining' ? 'bg-red-100' : 'bg-yellow-100'
                            }`}>
                            <div className="font-medium">Trend: {predictions.trend}</div>
                            <div className="text-sm">Confidence: {predictions.confidence}%</div>
                        </div>
                    )}
                </div>
            </div>

            {/* Correlation Analysis */}
            <div className="bg-white p-6 rounded-xl shadow-lg">
                <h4 className="font-semibold mb-4">🔄 Correlation Analysis</h4>
                <div className="space-y-3">
                    {performanceData.correlations?.map((correlation, index) => (
                        <div key={index} className="flex justify-between items-center p-3 border rounded">
                            <span className="text-sm">{correlation.metrics.join(' ↔ ')}</span>
                            <span className={`px-2 py-1 rounded text-xs ${Math.abs(correlation.correlation) > 0.7 ? 'bg-red-100' :
                                    Math.abs(correlation.correlation) > 0.3 ? 'bg-yellow-100' : 'bg-green-100'
                                }`}>
                                {correlation.correlation.toFixed(2)}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default PerformanceAnalyticsDashboard;
