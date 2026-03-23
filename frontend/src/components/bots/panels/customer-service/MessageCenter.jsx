// src/components/bots/panels/customer-service/MessageCenter.jsx
import React, { useState, useEffect } from 'react';
import { customerServiceAPI } from '../../../../services/customerService';
import './MessageCenter.css';

const MessageCenter = ({ onNotification }) => {
    const [activeTab, setActiveTab] = useState('templates');
    const [campaigns, setCampaigns] = useState([]);
    const [messageQueue, setMessageQueue] = useState([]);
    const [showCampaignForm, setShowCampaignForm] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [messageContent, setMessageContent] = useState('');
    const [loading, setLoading] = useState(false);

    const [formData, setFormData] = useState({
        name: '',
        type: 'broadcast',
        audience: 'all',
        audienceSize: 0,
        schedule: 'now',
        scheduledTime: ''
    });

    // Message templates with variables
    const messageTemplates = [
        {
            id: 1,
            name: 'Shipment Status Update',
            icon: '',
            template: 'Your shipment {{tracking_number}} is {{status}}. Location: {{location}}. ETA: {{eta}}',
            variables: ['tracking_number', 'status', 'location', 'eta'],
            category: 'logistics'
        },
        {
            id: 2,
            name: 'Delivery Appointment Confirmation',
            icon: '',
            template: 'Delivery appointment confirmed for {{tracking_number}} on {{delivery_date}} between {{time_window}}. Driver will call 30 min before arrival.',
            variables: ['tracking_number', 'delivery_date', 'time_window'],
            category: 'logistics'
        },
        {
            id: 3,
            name: 'Safety Alert for Drivers',
            icon: '',
            template: 'Safety Alert: {{route_name}}. Please check safety briefing: {{safety_url}}. Secure driving protects everyone.',
            variables: ['route_name', 'safety_url'],
            category: 'safety'
        },
        {
            id: 4,
            name: 'Automated Customer Support Response',
            icon: '',
            template: 'Thank you for contacting us! Your request has been received. Our team will assist you shortly. Support: {{support_phone}} | FAQ: {{faq_url}}',
            variables: ['support_phone', 'faq_url'],
            category: 'support'
        },
        {
            id: 5,
            name: 'Payment Reminder',
            icon: '',
            template: 'Reminder: Payment due for invoice {{invoice_number}} by {{due_date}}. Amount: {{amount}}. Pay now: {{payment_url}}',
            variables: ['invoice_number', 'due_date', 'amount', 'payment_url'],
            category: 'payment'
        },
        {
            id: 6,
            name: 'Payment Confirmation',
            icon: '',
            template: 'Payment received! Invoice {{invoice_number}} has been successfully paid. Amount: {{amount}}. Reference: {{reference_id}}',
            variables: ['invoice_number', 'amount', 'reference_id'],
            category: 'payment'
        }
    ];

    useEffect(() => {
        loadCampaigns();
        loadMessageQueue();
    }, []);

    const loadCampaigns = async () => {
        setLoading(true);
        try {
            const data = await customerServiceAPI.getCampaigns();
            setCampaigns(data);
        } catch (error) {
            console.error('Failed to load campaigns:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadMessageQueue = async () => {
        try {
            const data = await customerServiceAPI.getMessageQueue();
            setMessageQueue(data);
        } catch (error) {
            console.error('Failed to load message queue:', error);
        }
    };

    const selectTemplate = (template) => {
        setSelectedTemplate(template);
        setMessageContent(template.template);
        setActiveTab('compose');
    };

    const insertVariable = (variable) => {
        const placeholder = `{{${variable}}}`;
        setMessageContent(messageContent + placeholder);
    };

    const previewMessage = () => {
        let preview = selectedTemplate.template;
        selectedTemplate.variables.forEach(variable => {
            preview = preview.replace(`{{${variable}}}`, `[${variable}]`);
        });
        return preview;
    };

    const handleCreateCampaign = async () => {
        if (!formData.name || !messageContent) {
            onNotification('Please fill all required fields', '');
            return;
        }

        try {
            const campaignData = {
                ...formData,
                content: messageContent,
                template_id: selectedTemplate?.id
            };

            await customerServiceAPI.createCampaign(campaignData);
            onNotification('Campaign created successfully', '');

            setFormData({
                name: '',
                type: 'broadcast',
                audience: 'all',
                audienceSize: 0,
                schedule: 'now',
                scheduledTime: ''
            });
            setMessageContent('');
            setSelectedTemplate(null);
            setShowCampaignForm(false);
            loadCampaigns();
        } catch (error) {
            console.error('Failed to create campaign:', error);
            onNotification('Failed to create campaign', '');
        }
    };

    const launchCampaign = async (campaignId) => {
        try {
            await customerServiceAPI.launchCampaign(campaignId);
            onNotification('Campaign launched successfully', '');
            loadCampaigns();
        } catch (error) {
            console.error('Failed to launch campaign:', error);
        }
    };

    const testMessage = async (campaignId, phone) => {
        try {
            await customerServiceAPI.sendTestMessage(campaignId, phone);
            onNotification('Test message sent', '');
        } catch (error) {
            console.error('Failed to send test message:', error);
        }
    };

    return (
        <div className="message-center">
            {/* Tabs */}
            <div className="center-tabs">
                <button
                    className={`tab-btn ${activeTab === 'templates' ? 'active' : ''}`}
                    onClick={() => setActiveTab('templates')}
                >
                     Quick Templates
                </button>
                <button
                    className={`tab-btn ${activeTab === 'compose' ? 'active' : ''}`}
                    onClick={() => setActiveTab('compose')}
                >
                     Compose
                </button>
                <button
                    className={`tab-btn ${activeTab === 'campaigns' ? 'active' : ''}`}
                    onClick={() => setActiveTab('campaigns')}
                >
                     Campaigns
                </button>
                <button
                    className={`tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
                    onClick={() => setActiveTab('queue')}
                >
                     Message Queue
                </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
                {/* Templates Tab */}
                {activeTab === 'templates' && (
                    <div className="templates-tab">
                        <h3>Quick Message Templates</h3>
                        <div className="templates-grid">
                            {messageTemplates.map((template) => (
                                <div key={template.id} className="template-card">
                                    <div className="template-header">
                                        <span className="template-icon">{template.icon}</span>
                                        <span className="template-category">{template.category}</span>
                                    </div>
                                    <h4>{template.name}</h4>
                                    <p className="template-preview">{template.template}</p>
                                    <div className="template-variables">
                                        <small>Variables: {template.variables.join(', ')}</small>
                                    </div>
                                    <button
                                        className="use-template-btn"
                                        onClick={() => selectTemplate(template)}
                                    >
                                        Use Template 
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Compose Tab */}
                {activeTab === 'compose' && (
                    <div className="compose-tab">
                        {selectedTemplate ? (
                            <>
                                <div className="compose-header">
                                    <h3>{selectedTemplate.icon} {selectedTemplate.name}</h3>
                                    <button
                                        className="back-btn"
                                        onClick={() => {
                                            setSelectedTemplate(null);
                                            setMessageContent('');
                                        }}
                                    >
                                         Back to Templates
                                    </button>
                                </div>

                                <div className="compose-grid">
                                    {/* Message Editor */}
                                    <div className="editor-section">
                                        <label>Message Content</label>
                                        <textarea
                                            value={messageContent}
                                            onChange={(e) => setMessageContent(e.target.value)}
                                            placeholder="Edit your message..."
                                            className="message-editor"
                                        />

                                        {/* Variables Panel */}
                                        <div className="variables-section">
                                            <label>Insert Variables</label>
                                            <div className="variables-grid">
                                                {selectedTemplate.variables.map((variable) => (
                                                    <button
                                                        key={variable}
                                                        className="variable-btn"
                                                        onClick={() => insertVariable(variable)}
                                                    >
                                                        +{variable}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Campaign Form */}
                                        <div className="campaign-form">
                                            <h4>Campaign Details</h4>
                                            <div className="form-group">
                                                <label>Campaign Name</label>
                                                <input
                                                    type="text"
                                                    value={formData.name}
                                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                    placeholder="Enter campaign name"
                                                />
                                            </div>

                                            <div className="form-group">
                                                <label>Campaign Type</label>
                                                <select
                                                    value={formData.type}
                                                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                                >
                                                    <option value="broadcast">Broadcast</option>
                                                    <option value="automated">Automated</option>
                                                    <option value="triggered">Triggered</option>
                                                </select>
                                            </div>

                                            <div className="form-group">
                                                <label>Audience</label>
                                                <select
                                                    value={formData.audience}
                                                    onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                                                >
                                                    <option value="all">All Customers</option>
                                                    <option value="active">Active Only</option>
                                                    <option value="pending">Pending</option>
                                                    <option value="segment">Custom Segment</option>
                                                </select>
                                            </div>

                                            <div className="form-group">
                                                <label>Schedule</label>
                                                <select
                                                    value={formData.schedule}
                                                    onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                                                >
                                                    <option value="now">Send Now</option>
                                                    <option value="later">Schedule Later</option>
                                                    <option value="recurring">Recurring</option>
                                                </select>
                                            </div>

                                            {formData.schedule === 'later' && (
                                                <div className="form-group">
                                                    <label>Scheduled Time</label>
                                                    <input
                                                        type="datetime-local"
                                                        value={formData.scheduledTime}
                                                        onChange={(e) => setFormData({ ...formData, scheduledTime: e.target.value })}
                                                    />
                                                </div>
                                            )}

                                            <div className="form-actions">
                                                <button
                                                    className="save-btn"
                                                    onClick={handleCreateCampaign}
                                                >
                                                     Save Campaign
                                                </button>
                                                <button
                                                    className="preview-btn"
                                                    onClick={() => alert('Preview:\n\n' + previewMessage())}
                                                >
                                                     Preview
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Preview Section */}
                                    <div className="preview-section">
                                        <h4>Preview</h4>
                                        <div className="preview-box">
                                            <div className="preview-message">
                                                {previewMessage()}
                                            </div>
                                        </div>
                                        <div className="preview-info">
                                            <div className="info-item">
                                                <span className="label">Template:</span>
                                                <span className="value">{selectedTemplate.name}</span>
                                            </div>
                                            <div className="info-item">
                                                <span className="label">Variables:</span>
                                                <span className="value">{selectedTemplate.variables.length}</span>
                                            </div>
                                            <div className="info-item">
                                                <span className="label">Length:</span>
                                                <span className="value">{messageContent.length} chars</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="empty-state">
                                <span className="icon"></span>
                                <h3>Select a Template</h3>
                                <p>Go to "Quick Templates" tab and choose a template to start composing</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Campaigns Tab */}
                {activeTab === 'campaigns' && (
                    <div className="campaigns-tab">
                        <div className="campaigns-header">
                            <h3>Campaign Management</h3>
                            <button
                                className="new-campaign-btn"
                                onClick={() => setActiveTab('templates')}
                            >
                                 New Campaign
                            </button>
                        </div>

                        {campaigns.length > 0 ? (
                            <div className="campaigns-list">
                                {campaigns.map((campaign) => (
                                    <div key={campaign.id} className="campaign-item">
                                        <div className="campaign-info">
                                            <h4>{campaign.name}</h4>
                                            <div className="campaign-meta">
                                                <span className="type">{campaign.type}</span>
                                                <span className="status">{campaign.status}</span>
                                                <span className="date">{campaign.createdAt}</span>
                                            </div>
                                        </div>
                                        <div className="campaign-stats">
                                            <div className="stat">
                                                <span className="label">Sent</span>
                                                <span className="value">{campaign.sent || 0}</span>
                                            </div>
                                            <div className="stat">
                                                <span className="label">Delivered</span>
                                                <span className="value">{campaign.delivered || 0}</span>
                                            </div>
                                            <div className="stat">
                                                <span className="label">Opened</span>
                                                <span className="value">{campaign.opened || 0}</span>
                                            </div>
                                        </div>
                                        <div className="campaign-actions">
                                            {campaign.status === 'draft' && (
                                                <button
                                                    className="launch-btn"
                                                    onClick={() => launchCampaign(campaign.id)}
                                                >
                                                     Launch
                                                </button>
                                            )}
                                            <button
                                                className="test-btn"
                                                onClick={() => testMessage(campaign.id, '+1234567890')}
                                            >
                                                 Test
                                            </button>
                                            <button className="edit-btn"> Edit</button>
                                            <button className="delete-btn"> Delete</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <span className="icon"></span>
                                <h3>No Campaigns Yet</h3>
                                <p>Create your first campaign to get started</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Queue Tab */}
                {activeTab === 'queue' && (
                    <div className="queue-tab">
                        <h3>Message Queue</h3>
                        {messageQueue.length > 0 ? (
                            <div className="queue-list">
                                {messageQueue.map((msg) => (
                                    <div key={msg.id} className="queue-item">
                                        <div className="queue-icon">
                                            {msg.status === 'pending' ? '' : msg.status === 'sent' ? '' : ''}
                                        </div>
                                        <div className="queue-info">
                                            <div className="queue-recipient">{msg.recipient}</div>
                                            <div className="queue-message">{msg.message.substring(0, 60)}...</div>
                                        </div>
                                        <div className="queue-time">{msg.timestamp}</div>
                                        <div className="queue-status">{msg.status}</div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <span className="icon"></span>
                                <h3>Queue is Empty</h3>
                                <p>Messages will appear here when campaigns are sent</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MessageCenter;
