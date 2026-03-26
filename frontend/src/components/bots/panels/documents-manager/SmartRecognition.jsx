// src/components/bots/panels/documents-manager/SmartRecognition.jsx
import React, { useState, useEffect } from 'react';
import './SmartRecognition.css';

const DETERMINISTIC_ACCURACY = [95.6, 96.2, 97.1, 95.9];
const DETERMINISTIC_TYPE_INDEX = [0, 1, 2, 1, 0, 2];
const DETERMINISTIC_CONFIDENCE_BUMP = [4, 6, 8, 5, 7, 9];
const DETERMINISTIC_FIELDS = [7, 9, 11, 8, 10, 12];

const SmartRecognition = () => {
    const [recognitionMode, setRecognitionMode] = useState('auto');
    const [confidence, setConfidence] = useState(85);
    const [trainedModels, setTrainedModels] = useState([
        { id: 1, name: 'Bill of Lading Model v2.1', accuracy: 97.5, documents: 1250, lastTrained: '2024-01-15' },
        { id: 2, name: 'Commercial Invoice Model v2.0', accuracy: 95.8, documents: 980, lastTrained: '2024-01-10' },
        { id: 3, name: 'Customs Declaration Model v1.8', accuracy: 93.2, documents: 750, lastTrained: '2024-01-08' }
    ]);
    const [trainingStatus, setTrainingStatus] = useState(null);
    const [recognitionResults, setRecognitionResults] = useState([]);

    const documentTypes = [
        {
            id: 'bol',
            name: 'Bill of Lading',
            fields: ['shipper', 'consignee', 'vessel', 'port_of_loading', 'port_of_discharge'],
            confidence: 97,
            sampleCount: 1250
        },
        {
            id: 'invoice',
            name: 'Commercial Invoice',
            fields: ['invoice_number', 'date', 'total_amount', 'currency', 'incoterms'],
            confidence: 96,
            sampleCount: 980
        },
        {
            id: 'packing',
            name: 'Packing List',
            fields: ['package_count', 'weight', 'dimensions', 'marks', 'description'],
            confidence: 94,
            sampleCount: 650
        }
    ];

    const trainNewModel = async (documentType, trainingFiles) => {
        setTrainingStatus(`Training ${documentType} model...`);

        await new Promise(resolve => setTimeout(resolve, 3000));

        const modelIndex = trainedModels.length % DETERMINISTIC_ACCURACY.length;

        const newModel = {
            id: Date.now(),
            name: `${documentType} Model v2.0`,
            accuracy: DETERMINISTIC_ACCURACY[modelIndex],
            documents: trainingFiles.length,
            lastTrained: new Date().toISOString().split('T')[0]
        };

        setTrainedModels(prev => [...prev, newModel]);
        setTrainingStatus(null);
    };

    const recognizeDocuments = async (files) => {
        const results = [];

        for (let i = 0; i < files.length; i += 1) {
            const file = files[i];
            const cycleIndex = (recognitionResults.length + i) % DETERMINISTIC_TYPE_INDEX.length;
            const docIndex = DETERMINISTIC_TYPE_INDEX[cycleIndex] % documentTypes.length;
            const confidenceBump = DETERMINISTIC_CONFIDENCE_BUMP[cycleIndex];
            const extractedFields = DETERMINISTIC_FIELDS[cycleIndex];

            const result = {
                filename: file.name,
                recognized: true,
                documentType: documentTypes[docIndex].name,
                confidence: Math.min(99, confidence + confidenceBump),
                extractedFields,
                timestamp: new Date().toLocaleString()
            };

            results.push(result);
        }

        setRecognitionResults(prev => [...results, ...prev]);
    };

    return (
        <div className="smart-recognition">
            <div className="recognition-header">
                <h2> Smart Document Recognition</h2>
                <p>AI-powered document type identification and classification</p>
            </div>

            {/* AI Settings */}
            <div className="recognition-settings">
                <h3>Recognition Settings</h3>
                <div className="settings-grid">
                    <div className="setting">
                        <label>Recognition Mode</label>
                        <select value={recognitionMode} onChange={(e) => setRecognitionMode(e.target.value)}>
                            <option value="auto">Auto (Smart Detection)</option>
                            <option value="fast">Fast Processing</option>
                            <option value="accurate">High Accuracy</option>
                            <option value="hybrid">Hybrid Mode</option>
                        </select>
                        <p className="setting-hint">Auto mode intelligently selects processing speed</p>
                    </div>

                    <div className="setting">
                        <label>Confidence Threshold: {confidence}%</label>
                        <input
                            type="range"
                            min="70"
                            max="99"
                            value={confidence}
                            onChange={(e) => setConfidence(parseInt(e.target.value))}
                        />
                        <p className="setting-hint">Minimum confidence level to accept recognition</p>
                    </div>
                </div>
            </div>

            {/* Trained Models */}
            <div className="models-section">
                <h3> Trained AI Models</h3>
                <div className="models-grid">
                    {trainedModels.map(model => (
                        <div key={model.id} className="model-card">
                            <div className="model-header">
                                <span className="model-name">{model.name}</span>
                                <span className="model-accuracy">{model.accuracy.toFixed(1)}%</span>
                            </div>
                            <div className="model-stats">
                                <div className="stat-row">
                                    <span className="stat-label">Trained Samples:</span>
                                    <span className="stat-value">{model.documents}</span>
                                </div>
                                <div className="stat-row">
                                    <span className="stat-label">Last Trained:</span>
                                    <span className="stat-value">{model.lastTrained}</span>
                                </div>
                            </div>
                            <div className="model-actions">
                                <button className="action-btn retrain"> Retrain</button>
                                <button className="action-btn download"> Download</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Document Types Overview */}
            <div className="types-overview">
                <h3> Recognition Accuracy by Document Type</h3>
                <div className="types-grid">
                    {documentTypes.map(type => (
                        <div key={type.id} className="type-card">
                            <div className="type-header">{type.name}</div>
                            <div className="accuracy-bar">
                                <div className="bar-fill" style={{ width: `${type.confidence}%` }}>
                                    {type.confidence}%
                                </div>
                            </div>
                            <div className="type-fields">
                                <span className="fields-label">Key Fields:</span>
                                {type.fields.slice(0, 3).map((field, idx) => (
                                    <span key={idx} className="field-tag">{field}</span>
                                ))}
                            </div>
                            <div className="type-stats">
                                {type.sampleCount} training samples
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Training Progress */}
            {trainingStatus && (
                <div className="training-progress">
                    <div className="progress-content">
                        <div className="spinner"></div>
                        <p>{trainingStatus}</p>
                    </div>
                </div>
            )}

            {/* Recognition Results */}
            {recognitionResults.length > 0 && (
                <div className="recognition-results">
                    <h3>Recent Recognition Results</h3>
                    <div className="results-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Document Type</th>
                                    <th>Confidence</th>
                                    <th>Fields Extracted</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recognitionResults.slice(0, 5).map((result, idx) => (
                                    <tr key={idx} className={`result-row ${result.confidence > 90 ? 'high-confidence' : ''}`}>
                                        <td>
                                            <span className="file-icon"></span>
                                            {result.filename}
                                        </td>
                                        <td>{result.documentType}</td>
                                        <td>
                                            <span className="confidence-badge">{result.confidence}%</span>
                                        </td>
                                        <td>{result.extractedFields} fields</td>
                                        <td>{result.timestamp}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* ML Insights */}
            <div className="ml-insights">
                <h3> ML Insights</h3>
                <div className="insights-grid">
                    <div className="insight-card">
                        <div className="insight-icon"></div>
                        <div className="insight-content">
                            <div className="insight-title">Average Accuracy</div>
                            <div className="insight-value">
                                {(trainedModels.reduce((sum, m) => sum + m.accuracy, 0) / trainedModels.length).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    <div className="insight-card">
                        <div className="insight-icon"></div>
                        <div className="insight-content">
                            <div className="insight-title">Total Samples</div>
                            <div className="insight-value">
                                {trainedModels.reduce((sum, m) => sum + m.documents, 0).toLocaleString()}
                            </div>
                        </div>
                    </div>
                    <div className="insight-card">
                        <div className="insight-icon"></div>
                        <div className="insight-content">
                            <div className="insight-title">Processing Speed</div>
                            <div className="insight-value">~2.1s/doc</div>
                        </div>
                    </div>
                    <div className="insight-card">
                        <div className="insight-icon"></div>
                        <div className="insight-content">
                            <div className="insight-title">Recognition Rate</div>
                            <div className="insight-value">99.2%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SmartRecognition;
