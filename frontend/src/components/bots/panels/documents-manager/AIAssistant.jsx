// src/components/bots/panels/documents-manager/AIAssistant.jsx
import React, { useState, useRef, useEffect } from 'react';
import './AIAssistant.css';

const AIAssistant = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: 'assistant',
            content: 'Hello! I\'m your Documents Manager AI Assistant. I can help you with:',
            timestamp: new Date(),
            suggestions: [
                'Upload and organize documents',
                'Extract data with OCR',
                'Check compliance issues',
                'Generate reports',
                'Track document history',
                'Manage workflows'
            ]
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const quickActions = [
        { id: 1, icon: '', label: 'Upload Documents', description: 'Start uploading files' },
        { id: 2, icon: '', label: 'Search Documents', description: 'Find documents by name or content' },
        { id: 3, icon: '', label: 'Generate Report', description: 'Create analytics report' },
        { id: 4, icon: '', label: 'Check Compliance', description: 'Scan for compliance issues' },
        { id: 5, icon: '', label: 'Configure Workflow', description: 'Set up automation workflow' },
        { id: 6, icon: '', label: 'View History', description: 'Check document history' }
    ];

    const frequentQuestions = [
        'How do I upload multiple documents at once?',
        'What document formats are supported?',
        'Can I automate document processing?',
        'How do I verify document compliance?',
        'What is the storage limit?',
        'How can I export documents?'
    ];

    const handleSendMessage = async (text) => {
        if (!text.trim()) return;

        const userMessage = {
            id: messages.length + 1,
            role: 'user',
            content: text,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        // Simulate AI response
        await new Promise(resolve => setTimeout(resolve, 1500));

        const assistantResponses = [
            {
                content: 'I\'ve analyzed your request. Here are the top 3 recommendations:',
                items: [
                    '1. Use batch upload for multiple files (faster processing)',
                    '2. Enable OCR preprocessing for better data extraction',
                    '3. Set up automated compliance checking rules'
                ]
            },
            {
                content: 'You can organize documents by:',
                items: [
                    ' Document type (BOL, Invoice, etc.)',
                    ' Date range',
                    ' Compliance status',
                    ' Custom tags and folders'
                ]
            },
            {
                content: 'To improve document processing efficiency:',
                items: [
                    ' Enable batch processing',
                    ' Configure OCR language settings',
                    ' Set up workflow automation',
                    ' Use smart document recognition'
                ]
            }
        ];

        const response = assistantResponses[Math.floor((crypto.getRandomValues(new Uint32Array(1))[0] / 4294967296) * assistantResponses.length)];

        const assistantMessage = {
            id: messages.length + 2,
            role: 'assistant',
            content: response.content,
            items: response.items,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
    };

    const handleQuickAction = (action) => {
        handleSendMessage(`I want to ${action.label.toLowerCase()}`);
    };

    const handleFrequentQuestion = (question) => {
        handleSendMessage(question);
    };

    return (
        <div className="ai-assistant">
            <div className="assistant-header">
                <h2> AI Assistant</h2>
                <p>Get instant help with document management and automation</p>
            </div>

            <div className="assistant-container">
                {/* Sidebar with Quick Actions */}
                <div className="assistant-sidebar">
                    <div className="sidebar-section">
                        <h3>Quick Actions</h3>
                        <div className="quick-actions">
                            {quickActions.map(action => (
                                <button
                                    key={action.id}
                                    className="quick-action-btn"
                                    onClick={() => handleQuickAction(action)}
                                    title={action.description}
                                >
                                    <div className="action-icon">{action.icon}</div>
                                    <div className="action-label">{action.label}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="sidebar-section">
                        <h3>Frequently Asked</h3>
                        <div className="faq-list">
                            {frequentQuestions.map((question, idx) => (
                                <button
                                    key={idx}
                                    className="faq-btn"
                                    onClick={() => handleFrequentQuestion(question)}
                                    title={question}
                                >
                                    <span className="faq-icon"></span>
                                    <span className="faq-text">{question}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="chat-area">
                    <div className="messages-container">
                        {messages.map(message => (
                            <div key={message.id} className={`message ${message.role}`}>
                                <div className="message-icon">
                                    {message.role === 'user' ? '' : ''}
                                </div>
                                <div className="message-content">
                                    <div className="message-text">{message.content}</div>

                                    {message.suggestions && message.suggestions.length > 0 && (
                                        <div className="suggestions-list">
                                            {message.suggestions.map((suggestion, idx) => (
                                                <button
                                                    key={idx}
                                                    className="suggestion-btn"
                                                    onClick={() => handleSendMessage(suggestion)}
                                                >
                                                    {suggestion}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    {message.items && message.items.length > 0 && (
                                        <div className="items-list">
                                            {message.items.map((item, idx) => (
                                                <div key={idx} className="item">{item}</div>
                                            ))}
                                        </div>
                                    )}

                                    <div className="message-time">
                                        {message.timestamp.toLocaleTimeString([], {
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="message assistant loading">
                                <div className="message-icon"></div>
                                <div className="message-content">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="input-area">
                        <div className="input-wrapper">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && !isLoading) {
                                        handleSendMessage(inputValue);
                                    }
                                }}
                                placeholder="Ask me anything about document management..."
                                className="chat-input"
                                disabled={isLoading}
                            />
                            <button
                                onClick={() => handleSendMessage(inputValue)}
                                disabled={isLoading || !inputValue.trim()}
                                className="send-btn"
                            >
                                
                            </button>
                        </div>
                        <div className="input-hints">
                            <span> Tip: Ask about uploading, organizing, searching, or automating documents</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* AI Capabilities */}
            <div className="ai-capabilities">
                <h3> AI Capabilities</h3>
                <div className="capabilities-grid">
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Document Analysis</div>
                        <div className="capability-desc">Intelligent document type recognition and data extraction</div>
                    </div>
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Smart Search</div>
                        <div className="capability-desc">Find documents by content, keywords, or document type</div>
                    </div>
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Workflow Automation</div>
                        <div className="capability-desc">Create and optimize document processing workflows</div>
                    </div>
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Compliance Checking</div>
                        <div className="capability-desc">Automatic validation against compliance rules</div>
                    </div>
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Analytics Insights</div>
                        <div className="capability-desc">Predictive analytics and performance recommendations</div>
                    </div>
                    <div className="capability-card">
                        <div className="capability-icon"></div>
                        <div className="capability-title">Security Advisory</div>
                        <div className="capability-desc">Recommendations for document security and privacy</div>
                    </div>
                </div>
            </div>

            {/* AI Settings */}
            <div className="ai-settings">
                <h3> AI Assistant Settings</h3>
                <div className="settings-grid">
                    <div className="setting">
                        <label>Automation Level</label>
                        <select>
                            <option>Suggestions Only</option>
                            <option>Semi-Automated</option>
                            <option>Fully Automated</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>Response Detail</label>
                        <select>
                            <option>Brief</option>
                            <option>Standard</option>
                            <option>Detailed</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>Learning Mode</label>
                        <select>
                            <option>Enabled</option>
                            <option>Disabled</option>
                        </select>
                    </div>
                    <div className="setting">
                        <label>Language</label>
                        <select>
                            <option>English</option>
                            <option>Arabic</option>
                            <option>French</option>
                            <option>Spanish</option>
                        </select>
                    </div>
                </div>
                <button className="save-settings-btn"> Save Settings</button>
            </div>
        </div>
    );
};

export default AIAssistant;
