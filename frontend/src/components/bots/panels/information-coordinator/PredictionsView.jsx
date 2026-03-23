// Predictions View Component
import React, { useState, useEffect } from 'react';
import informationService from '../../../../services/informationService';
import './OperationalDashboard.css';

const PredictionsView = ({ onNewNotification, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [predictionType, setPredictionType] = useState('demand');
    const [predictions, setPredictions] = useState(null);

    useEffect(() => {
        loadPredictions();
    }, [predictionType, refreshKey]);

    const loadPredictions = async () => {
        setLoading(true);
        try {
            let data;
            switch (predictionType) {
                case 'demand':
                    data = await informationService.predictDemand('next_7_days');
                    break;
                case 'revenue':
                    data = await informationService.predictRevenue('next_30_days');
                    break;
                case 'inventory':
                    data = await informationService.predictInventoryNeeds();
                    break;
                default:
                    data = null;
            }
            setPredictions(data);
        } catch (error) {
            onNewNotification?.('Failed to load predictions', 'error');
        } finally {
            setLoading(false);
        }
    };

    const predictionTypes = [
        { id: 'demand', name: 'Demand Forecast', icon: '', description: 'Predict shipment volumes' },
        { id: 'revenue', name: 'Revenue Forecast', icon: '', description: 'Predict financial performance' },
        { id: 'inventory', name: 'Inventory Needs', icon: '', description: 'Predict inventory requirements' }
    ];

    return (
        <div className="predictions-view">
            {/* Prediction Type Selector */}
            <div className="prediction-types">
                {predictionTypes.map(type => (
                    <button
                        key={type.id}
                        className={`prediction-type-card ${predictionType === type.id ? 'active' : ''}`}
                        onClick={() => setPredictionType(type.id)}
                    >
                        <span className="type-icon">{type.icon}</span>
                        <div className="type-info">
                            <h3>{type.name}</h3>
                            <p>{type.description}</p>
                        </div>
                    </button>
                ))}
            </div>

            {/* Predictions Content */}
            {loading ? (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Generating predictions...</p>
                </div>
            ) : predictions ? (
                <div className="predictions-content">
                    <div className="predictions-header">
                        <h3> AI-Powered Predictions</h3>
                        <span className="confidence-badge">
                            Confidence: {predictions.confidence || 'Medium'}
                        </span>
                    </div>

                    {predictions.predictions && (
                        <div className="predictions-results">
                            {predictionType === 'demand' && predictions.predictions.next_7_days_revenue && (
                                <div className="prediction-chart">
                                    <h4>Next 7 Days Revenue Forecast</h4>
                                    <div className="chart-bars">
                                        {predictions.predictions.next_7_days_revenue.map((value, index) => (
                                            <div key={index} className="chart-bar-container">
                                                <div
                                                    className="chart-bar"
                                                    style={{ height: `${(value / Math.max(...predictions.predictions.next_7_days_revenue)) * 100}%` }}
                                                >
                                                    <span className="bar-value">${value.toLocaleString()}</span>
                                                </div>
                                                <span className="bar-label">Day {index + 1}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="chart-summary">
                                        <div className="summary-item">
                                            <span className="summary-label">Avg Daily Revenue</span>
                                            <span className="summary-value">
                                                ${predictions.predictions.avg_daily_revenue?.toLocaleString() || 0}
                                            </span>
                                        </div>
                                        <div className="summary-item">
                                            <span className="summary-label">Avg Daily Shipments</span>
                                            <span className="summary-value">
                                                {predictions.predictions.avg_daily_shipments || 0}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="predictions-json">
                                <h4>Detailed Predictions</h4>
                                <pre>{JSON.stringify(predictions.predictions, null, 2)}</pre>
                            </div>

                            {predictions.assumptions && (
                                <div className="predictions-assumptions">
                                    <h4>Assumptions</h4>
                                    <ul>
                                        {predictions.assumptions.map((assumption, index) => (
                                            <li key={index}>{assumption}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    <div className="predictions-note">
                        <span className="note-icon"></span>
                        <p>These predictions are generated using machine learning models based on historical data. Actual results may vary.</p>
                    </div>
                </div>
            ) : (
                <div className="empty-state">
                    <span className="empty-icon"></span>
                    <p>No predictions available</p>
                    <p className="empty-hint">Backend integration required for AI-powered forecasting</p>
                </div>
            )}
        </div>
    );
};

export default PredictionsView;
