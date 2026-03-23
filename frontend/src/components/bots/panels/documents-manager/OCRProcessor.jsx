// src/components/bots/panels/documents-manager/OCRProcessor.jsx
import React, { useState, useEffect } from 'react';
import './OCRProcessor.css';
import documentsService from '../../../../services/documentsService';

const OCRProcessor = () => {
    const [processingQueue, setProcessingQueue] = useState([]);
    const [processedDocs, setProcessedDocs] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [ocrConfig, setOcrConfig] = useState({
        language: 'eng+ara',
        accuracy: 'high',
        extractTables: true,
        extractSignatures: true,
        autoCategorize: true
    });

    useEffect(() => {
        loadProcessingQueue();
    }, []);

    const loadProcessingQueue = async () => {
        try {
            const queue = await documentsService.getProcessingQueue();
            const processed = await documentsService.getProcessedDocuments();
            setProcessingQueue(queue);
            setProcessedDocs(processed);
        } catch (error) {
            console.error('Failed to load OCR queue:', error);
        }
    };

    const startProcessing = async () => {
        if (processingQueue.length === 0) return;

        setIsProcessing(true);
        try {
            await documentsService.processAll(processingQueue);
            await loadProcessingQueue();
        } catch (error) {
            console.error('Failed to process queue:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    const processSingleDocument = async (docId) => {
        try {
            await documentsService.processSingle(docId);
            await loadProcessingQueue();
        } catch (error) {
            console.error('Failed to process document:', error);
        }
    };

    const OcrResultViewer = ({ doc }) => (
        <div className="ocr-result">
            <div className="result-header">
                <h4>Extracted Data</h4>
                <span className="accuracy">Accuracy: {doc.accuracy.toFixed(1)}%</span>
            </div>

            <div className="extracted-fields">
                <div className="field-row">
                    <span className="field-label">Document Type:</span>
                    <span className="field-value">{doc.type}</span>
                </div>
                <div className="field-row">
                    <span className="field-label">Shipment Number:</span>
                    <span className="field-value">SHIP-789456</span>
                </div>
                <div className="field-row">
                    <span className="field-label">Shipper:</span>
                    <span className="field-value">ABC Manufacturing Co.</span>
                </div>
                <div className="field-row">
                    <span className="field-label">Consignee:</span>
                    <span className="field-value">XYZ Logistics Inc.</span>
                </div>
                <div className="field-row">
                    <span className="field-label">Total Amount:</span>
                    <span className="field-value">$12,500.00</span>
                </div>
            </div>

            <button className="view-details-btn">View All Extracted Data</button>
        </div>
    );

    return (
        <div className="ocr-processor">
            <div className="ocr-header">
                <h2>OCR Processing</h2>
                <p>Optical Character Recognition for automated document data extraction</p>
            </div>

            <div className="ocr-configuration">
                <h3>Configuration Settings</h3>
                <div className="config-grid">
                    <div className="config-group">
                        <label>OCR Language</label>
                        <select
                            value={ocrConfig.language}
                            onChange={(e) => setOcrConfig({ ...ocrConfig, language: e.target.value })}
                        >
                            <option value="eng">English</option>
                            <option value="ara">Arabic</option>
                            <option value="eng+ara">English + Arabic</option>
                            <option value="multi">Multiple Languages</option>
                        </select>
                    </div>

                    <div className="config-group">
                        <label>Accuracy Level</label>
                        <select
                            value={ocrConfig.accuracy}
                            onChange={(e) => setOcrConfig({ ...ocrConfig, accuracy: e.target.value })}
                        >
                            <option value="fast">Fast (Lower Accuracy)</option>
                            <option value="balanced">Balanced</option>
                            <option value="high">High Accuracy</option>
                            <option value="maximum">Maximum Accuracy</option>
                        </select>
                    </div>

                    <div className="config-checkboxes">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={ocrConfig.extractTables}
                                onChange={(e) => setOcrConfig({ ...ocrConfig, extractTables: e.target.checked })}
                            />
                            <span>Extract Tables</span>
                        </label>

                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={ocrConfig.extractSignatures}
                                onChange={(e) => setOcrConfig({ ...ocrConfig, extractSignatures: e.target.checked })}
                            />
                            <span>Detect Signatures</span>
                        </label>

                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={ocrConfig.autoCategorize}
                                onChange={(e) => setOcrConfig({ ...ocrConfig, autoCategorize: e.target.checked })}
                            />
                            <span>Auto-categorize Documents</span>
                        </label>
                    </div>
                </div>

                <button
                    className="save-config-btn"
                    onClick={async () => {
                        await documentsService.saveOcrConfig(ocrConfig);
                        alert(' OCR configuration saved');
                    }}
                >
                     Save Configuration
                </button>
            </div>

            <div className="processing-section">
                <div className="section-header">
                    <h3>Processing Queue ({processingQueue.length} documents)</h3>
                    <div className="section-actions">
                        <button
                            className={`process-all-btn ${isProcessing ? 'processing' : ''}`}
                            onClick={startProcessing}
                            disabled={isProcessing || processingQueue.length === 0}
                        >
                            {isProcessing ? ' Processing...' : ' Process All'}
                        </button>
                        <button className="refresh-btn" onClick={loadProcessingQueue}>
                             Refresh
                        </button>
                    </div>
                </div>

                {processingQueue.length === 0 ? (
                    <div className="empty-queue">
                        <span className="empty-icon"></span>
                        <p>No documents in processing queue</p>
                        <p className="empty-subtext">Upload documents to start OCR processing</p>
                    </div>
                ) : (
                    <div className="queue-list">
                        {processingQueue.map(doc => (
                            <div key={doc.id} className="queue-item">
                                <div className="queue-doc-info">
                                    <div className="doc-icon"></div>
                                    <div className="doc-details">
                                        <div className="doc-name">{doc.name}</div>
                                        <div className="doc-meta">
                                            <span className="meta-item">
                                                <span className="meta-label">Type:</span>
                                                <span className="meta-value">{doc.type}</span>
                                            </span>
                                            <span className="meta-item">
                                                <span className="meta-label">Pages:</span>
                                                <span className="meta-value">{doc.pages}</span>
                                            </span>
                                            <span className="meta-item">
                                                <span className="meta-label">Size:</span>
                                                <span className="meta-value">{doc.size}</span>
                                            </span>
                                            <span className={`priority-badge ${doc.priority}`}>
                                                {doc.priority}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="queue-actions">
                                    <button
                                        className="process-btn"
                                        onClick={() => processSingleDocument(doc.id)}
                                        disabled={isProcessing}
                                    >
                                         Process
                                    </button>
                                    <button
                                        className="cancel-btn"
                                        onClick={() => setProcessingQueue(prev => prev.filter(d => d.id !== doc.id))}
                                    >
                                         Remove
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="processed-section">
                <h3>Recently Processed Documents</h3>

                {processedDocs.length === 0 ? (
                    <div className="empty-processed">
                        <span className="empty-icon"></span>
                        <p>No documents processed yet</p>
                    </div>
                ) : (
                    <div className="processed-list">
                        {processedDocs.map(doc => (
                            <div key={doc.id} className="processed-item">
                                <div className="processed-header">
                                    <div className="doc-info">
                                        <span className="doc-icon"></span>
                                        <span className="doc-name">{doc.name}</span>
                                        <span className={`status-badge ${doc.status}`}>
                                            {doc.status}
                                        </span>
                                    </div>
                                    <div className="doc-stats">
                                        <span className="stat">
                                            <span className="stat-label">Fields:</span>
                                            <span className="stat-value">{doc.extractedFields}</span>
                                        </span>
                                        <span className="stat">
                                            <span className="stat-label">Accuracy:</span>
                                            <span className="stat-value">{doc.accuracy.toFixed(1)}%</span>
                                        </span>
                                        <span className="stat">
                                            <span className="stat-label">Processed:</span>
                                            <span className="stat-value">{doc.processed}</span>
                                        </span>
                                    </div>
                                </div>

                                <div className="processed-content">
                                    <OcrResultViewer doc={doc} />
                                </div>

                                <div className="processed-actions">
                                    <button className="action-btn">
                                         Edit Extracted Data
                                    </button>
                                    <button className="action-btn">
                                         Export as JSON
                                    </button>
                                    <button className="action-btn">
                                         Re-process
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="ocr-statistics">
                <h3>Processing Statistics</h3>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">{processedDocs.length}</div>
                        <div className="stat-label">Documents Processed</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">100%</div>
                        <div className="stat-label">Success Rate</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">2.3s</div>
                        <div className="stat-label">Avg Processing Time</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon"></div>
                        <div className="stat-value">97.8%</div>
                        <div className="stat-label">Average Accuracy</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OCRProcessor;
