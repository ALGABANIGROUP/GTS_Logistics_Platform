// src/components/bots/panels/customer-service/SocialCampaignManager.jsx
import React, { useState, useEffect } from 'react';
import { socialMediaAPI } from '../../../../services/socialMediaService';
import './SocialCampaignManager.css';

const SocialCampaignManager = ({ onNewNotification }) => {
    const [socialCampaigns, setSocialCampaigns] = useState([]);
    const [platforms, setPlatforms] = useState([
        { id: 'facebook', name: 'Facebook', icon: '', connected: false },
        { id: 'instagram', name: 'Instagram', icon: '', connected: false },
        { id: 'twitter', name: 'Twitter', icon: '', connected: false },
        { id: 'linkedin', name: 'LinkedIn', icon: '', connected: false },
        { id: 'whatsapp', name: 'WhatsApp Business', icon: '', connected: false },
        { id: 'tiktok', name: 'TikTok', icon: '', connected: false }
    ]);
    const [selectedPlatform, setSelectedPlatform] = useState('facebook');
    const [newCampaign, setNewCampaign] = useState({
        name: '',
        platform: 'facebook',
        objective: 'awareness',
        audience: 'custom',
        budget: 100,
        schedule: {
            startDate: new Date().toISOString().split('T')[0],
            endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            time: '09:00'
        },
        content: {
            text: '',
            media: [],
            hashtags: [],
            cta: 'learn_more'
        }
    });
    const [analytics, setAnalytics] = useState({
        totalReach: 0,
        engagements: 0,
        clicks: 0,
        conversions: 0,
        roi: '0%'
    });
    const [activeTab, setActiveTab] = useState('campaigns');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadSocialCampaigns();
        loadAnalytics();
    }, []);

    const loadSocialCampaigns = async () => {
        setLoading(true);
        try {
            const campaigns = await socialMediaAPI.getCampaigns();
            setSocialCampaigns(campaigns);
        } catch (error) {
            console.error('Failed to load social campaigns:', error);
            onNewNotification('Failed to load campaigns', '');
        } finally {
            setLoading(false);
        }
    };

    const loadAnalytics = async () => {
        try {
            const stats = await socialMediaAPI.getAnalytics();
            setAnalytics(stats);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    };

    const connectPlatform = async (platformId) => {
        try {
            const result = await socialMediaAPI.connectPlatform(platformId);

            if (result.success) {
                setPlatforms(prev =>
                    prev.map(platform =>
                        platform.id === platformId
                            ? { ...platform, connected: true }
                            : platform
                    )
                );

                onNewNotification(`${platformId.toUpperCase()} connected successfully`, '');
            }
        } catch (error) {
            console.error(`Failed to connect ${platformId}:`, error);
            onNewNotification(`Failed to connect ${platformId}`, '');
        }
    };

    const createSocialCampaign = async () => {
        if (!newCampaign.name.trim() || !newCampaign.content.text.trim()) {
            onNewNotification('Campaign name and content are required', '');
            return;
        }

        setLoading(true);
        try {
            const campaign = await socialMediaAPI.createCampaign(newCampaign);
            setSocialCampaigns(prev => [campaign, ...prev]);

            onNewNotification(`New social campaign created: ${campaign.name}`, '');

            // Reset form
            setNewCampaign({
                name: '',
                platform: 'facebook',
                objective: 'awareness',
                audience: 'custom',
                budget: 100,
                schedule: {
                    startDate: new Date().toISOString().split('T')[0],
                    endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    time: '09:00'
                },
                content: {
                    text: '',
                    media: [],
                    hashtags: [],
                    cta: 'learn_more'
                }
            });
        } catch (error) {
            console.error('Failed to create social campaign:', error);
            onNewNotification('Failed to create campaign', '');
        } finally {
            setLoading(false);
        }
    };

    const publishImmediately = async (campaignId) => {
        setLoading(true);
        try {
            await socialMediaAPI.publishCampaign(campaignId);
            setSocialCampaigns(prev =>
                prev.map(camp =>
                    camp.id === campaignId
                        ? { ...camp, status: 'published', published_at: new Date().toISOString() }
                        : camp
                )
            );

            onNewNotification('Campaign published successfully!', '');
        } catch (error) {
            console.error('Failed to publish campaign:', error);
            onNewNotification('Failed to publish campaign', '');
        } finally {
            setLoading(false);
        }
    };

    const scheduleCampaign = async (campaignId, schedule) => {
        setLoading(true);
        try {
            await socialMediaAPI.scheduleCampaign(campaignId, schedule);
            setSocialCampaigns(prev =>
                prev.map(camp =>
                    camp.id === campaignId
                        ? { ...camp, status: 'scheduled', scheduled_for: schedule }
                        : camp
                )
            );

            onNewNotification('Campaign scheduled successfully!', '');
        } catch (error) {
            console.error('Failed to schedule campaign:', error);
            onNewNotification('Failed to schedule campaign', '');
        } finally {
            setLoading(false);
        }
    };

    const boostCampaign = async (campaignId) => {
        setLoading(true);
        try {
            await socialMediaAPI.boostCampaign(campaignId, { budget_increase: 100 });
            onNewNotification('Campaign boosted successfully!', '');
            loadAnalytics();
        } catch (error) {
            console.error('Failed to boost campaign:', error);
            onNewNotification('Failed to boost campaign', '');
        } finally {
            setLoading(false);
        }
    };

    const campaignObjectives = [
        { id: 'awareness', name: 'Brand Awareness', icon: '', description: 'Increase brand visibility' },
        { id: 'engagement', name: 'Engagement', icon: '', description: 'Boost likes, comments, shares' },
        { id: 'traffic', name: 'Website Traffic', icon: '', description: 'Drive visitors to website' },
        { id: 'leads', name: 'Lead Generation', icon: '', description: 'Collect customer leads' },
        { id: 'sales', name: 'Sales', icon: '', description: 'Increase product sales' },
        { id: 'support', name: 'Customer Support', icon: '', description: 'Provide customer service' }
    ];

    const prebuiltAudiences = [
        { id: 'logistics_customers', name: 'Logistics Customers', size: '15K', description: 'Active shipping customers' },
        { id: 'business_owners', name: 'Business Owners', size: '50K', description: 'SME business owners' },
        { id: 'international_shippers', name: 'International Shippers', size: '8K', description: 'Cross-border shipping clients' },
        { id: 'frequent_shippers', name: 'Frequent Shippers', size: '25K', description: 'Monthly active shippers' },
        { id: 'new_customers', name: 'New Customers', size: '5K', description: 'Customers from last 30 days' }
    ];

    const contentTemplates = [
        {
            id: 'shipment_update',
            name: 'Shipment Status Update',
            platform: 'all',
            template: ` Your shipment #{tracking_number} is on the way! 
 Current status: {status}
 Location: {location}
 ETA: {delivery_date}

Track your shipment: {tracking_url}
#GTSLogistics #Shipping #DeliveryUpdate`,
            variables: ['tracking_number', 'status', 'location', 'delivery_date', 'tracking_url']
        },
        {
            id: 'service_announcement',
            name: 'Service Announcement',
            platform: 'all',
            template: ` New Service Announcement!
We're excited to introduce {new_service} to make your shipping easier!

 {benefit_1}
 {benefit_2}
 {benefit_3}

Learn more: {service_url}
#GTSLogistics #NewService #Shipping`,
            variables: ['new_service', 'benefit_1', 'benefit_2', 'benefit_3', 'service_url']
        },
        {
            id: 'customer_testimonial',
            name: 'Customer Testimonial',
            platform: 'instagram',
            template: ` Customer Spotlight 

"{testimonial_text}"

- {customer_name}, {customer_business}

Thank you for trusting Gabani Transport Solutions (GTS) with your shipping needs! 

#CustomerSuccess #Testimonial #GTSLogistics #Shipping`,
            variables: ['testimonial_text', 'customer_name', 'customer_business']
        },
        {
            id: 'safety_tip',
            name: 'Safety Tip',
            platform: 'facebook',
            template: ` Safety First! 

{tip_title}

{tip_description}

Remember: {safety_reminder}

#SafetyFirst #LogisticsSafety #GTSLogistics #Trucking`,
            variables: ['tip_title', 'tip_description', 'safety_reminder']
        }
    ];

    return (
        <div className="social-campaign-manager">
            {/* Header */}
            <div className="campaign-header">
                <h2> Social Media Campaign Manager</h2>
                <div className="header-stats">
                    <span className="stat">Active: {socialCampaigns.filter(c => c.status === 'active').length}</span>
                    <span className="stat">Reach: {analytics.totalReach.toLocaleString()}</span>
                    <span className="stat">Engagement: {((analytics.engagements / (analytics.totalReach || 1)) * 100).toFixed(2)}%</span>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="tab-navigation">
                <button
                    className={`tab-btn ${activeTab === 'campaigns' ? 'active' : ''}`}
                    onClick={() => setActiveTab('campaigns')}
                >
                     Campaigns
                </button>
                <button
                    className={`tab-btn ${activeTab === 'platforms' ? 'active' : ''}`}
                    onClick={() => setActiveTab('platforms')}
                >
                     Platforms
                </button>
                <button
                    className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('analytics')}
                >
                     Analytics
                </button>
            </div>

            {/* Platforms Tab */}
            {activeTab === 'platforms' && (
                <div className="platforms-section">
                    <h3>Connected Platforms</h3>
                    <div className="platforms-grid">
                        {platforms.map((platform) => (
                            <div key={platform.id} className={`platform-card ${platform.connected ? 'connected' : 'disconnected'}`}>
                                <div className="platform-icon">{platform.icon}</div>
                                <div className="platform-info">
                                    <div className="platform-name">{platform.name}</div>
                                    <div className="platform-status">
                                        <span className={`status-dot ${platform.connected ? 'connected' : 'disconnected'}`}></span>
                                        {platform.connected ? 'Connected' : 'Not Connected'}
                                    </div>
                                </div>
                                {!platform.connected && (
                                    <button
                                        className="connect-btn"
                                        onClick={() => connectPlatform(platform.id)}
                                        disabled={loading}
                                    >
                                        Connect
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Campaigns Tab */}
            {activeTab === 'campaigns' && (
                <div className="campaign-layout">
                    {/* Campaign Creation Form */}
                    <div className="campaign-creator-form">
                        <h3>Create New Campaign</h3>

                        <div className="form-section">
                            <label>Campaign Name *</label>
                            <input
                                type="text"
                                placeholder="e.g., Q1 Shipping Promotion"
                                value={newCampaign.name}
                                onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                            />
                        </div>

                        <div className="form-section">
                            <label>Platform</label>
                            <div className="platform-selector">
                                {platforms.filter(p => p.connected).map((platform) => (
                                    <button
                                        key={platform.id}
                                        className={`platform-btn ${selectedPlatform === platform.id ? 'selected' : ''}`}
                                        onClick={() => {
                                            setSelectedPlatform(platform.id);
                                            setNewCampaign({ ...newCampaign, platform: platform.id });
                                        }}
                                    >
                                        {platform.icon} {platform.name}
                                    </button>
                                ))}
                            </div>
                            {platforms.filter(p => p.connected).length === 0 && (
                                <p className="info-text"> Connect platforms first</p>
                            )}
                        </div>

                        <div className="form-section">
                            <label>Campaign Objective</label>
                            <div className="objectives-grid">
                                {campaignObjectives.map((obj) => (
                                    <div
                                        key={obj.id}
                                        className={`objective-card ${newCampaign.objective === obj.id ? 'selected' : ''}`}
                                        onClick={() => setNewCampaign({ ...newCampaign, objective: obj.id })}
                                    >
                                        <div className="objective-icon">{obj.icon}</div>
                                        <div className="objective-name">{obj.name}</div>
                                        <div className="objective-desc">{obj.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="form-section">
                            <label>Target Audience</label>
                            <select
                                value={newCampaign.audience}
                                onChange={(e) => setNewCampaign({ ...newCampaign, audience: e.target.value })}
                            >
                                <option value="custom">Custom Audience</option>
                                {prebuiltAudiences.map((audience) => (
                                    <option key={audience.id} value={audience.id}>
                                        {audience.name} ({audience.size})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="form-section">
                            <label>Budget</label>
                            <div className="budget-control">
                                <input
                                    type="range"
                                    min="50"
                                    max="10000"
                                    step="50"
                                    value={newCampaign.budget}
                                    onChange={(e) => setNewCampaign({ ...newCampaign, budget: parseInt(e.target.value) })}
                                />
                                <div className="budget-display">
                                    <span className="budget-amount">${newCampaign.budget}</span>
                                    <span className="budget-period">/ campaign</span>
                                </div>
                            </div>
                        </div>

                        <div className="form-section">
                            <label>Campaign Content *</label>
                            <div className="content-templates">
                                <h4>Quick Templates</h4>
                                <div className="templates-grid">
                                    {contentTemplates
                                        .filter(t => t.platform === 'all' || t.platform === selectedPlatform)
                                        .map((template) => (
                                            <div
                                                key={template.id}
                                                className="template-card"
                                                onClick={() => setNewCampaign({
                                                    ...newCampaign,
                                                    content: {
                                                        ...newCampaign.content,
                                                        text: template.template
                                                    }
                                                })}
                                            >
                                                <div className="template-name">{template.name}</div>
                                                <div className="template-preview">
                                                    {template.template.substring(0, 80)}...
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </div>

                            <textarea
                                className="content-editor"
                                placeholder="Write your campaign content here..."
                                value={newCampaign.content.text}
                                onChange={(e) => setNewCampaign({
                                    ...newCampaign,
                                    content: { ...newCampaign.content, text: e.target.value }
                                })}
                                rows={6}
                            />
                        </div>

                        <div className="form-section">
                            <label>Schedule</label>
                            <div className="schedule-controls">
                                <div className="schedule-input">
                                    <label>Start Date</label>
                                    <input
                                        type="date"
                                        value={newCampaign.schedule.startDate}
                                        onChange={(e) => setNewCampaign({
                                            ...newCampaign,
                                            schedule: { ...newCampaign.schedule, startDate: e.target.value }
                                        })}
                                    />
                                </div>
                                <div className="schedule-input">
                                    <label>End Date</label>
                                    <input
                                        type="date"
                                        value={newCampaign.schedule.endDate}
                                        onChange={(e) => setNewCampaign({
                                            ...newCampaign,
                                            schedule: { ...newCampaign.schedule, endDate: e.target.value }
                                        })}
                                    />
                                </div>
                                <div className="schedule-input">
                                    <label>Post Time</label>
                                    <input
                                        type="time"
                                        value={newCampaign.schedule.time}
                                        onChange={(e) => setNewCampaign({
                                            ...newCampaign,
                                            schedule: { ...newCampaign.schedule, time: e.target.value }
                                        })}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="form-actions">
                            <button className="save-draft-btn"> Save Draft</button>
                            <button
                                className="schedule-btn"
                                onClick={() => scheduleCampaign('new', newCampaign.schedule)}
                                disabled={loading}
                            >
                                 Schedule
                            </button>
                            <button
                                className="publish-btn"
                                onClick={createSocialCampaign}
                                disabled={loading || !newCampaign.name || !newCampaign.content.text}
                            >
                                {loading ? ' Publishing...' : ' Publish Now'}
                            </button>
                        </div>
                    </div>

                    {/* Campaigns List */}
                    <div className="campaigns-list-section">
                        <h3>Your Campaigns ({socialCampaigns.length})</h3>
                        {loading && <p className="loading-text">Loading campaigns...</p>}
                        <div className="campaigns-list">
                            {socialCampaigns.map((campaign) => (
                                <div key={campaign.id} className="campaign-item">
                                    <div className="campaign-header">
                                        <div className="campaign-platform">
                                            <span className="platform-icon">
                                                {platforms.find(p => p.id === campaign.platform)?.icon || ''}
                                            </span>
                                            <span className="platform-name">
                                                {platforms.find(p => p.id === campaign.platform)?.name}
                                            </span>
                                        </div>
                                        <span className={`campaign-status ${campaign.status}`}>
                                            {campaign.status}
                                        </span>
                                    </div>

                                    <div className="campaign-body">
                                        <h4 className="campaign-name">{campaign.name}</h4>
                                        <p className="campaign-objective">
                                            Goal: {campaignObjectives.find(o => o.id === campaign.objective)?.name}
                                        </p>

                                        <div className="campaign-stats">
                                            <div className="stat">
                                                <span className="stat-label">Reach</span>
                                                <span className="stat-value">{campaign.reach?.toLocaleString() || '0'}</span>
                                            </div>
                                            <div className="stat">
                                                <span className="stat-label">Engagements</span>
                                                <span className="stat-value">{campaign.engagements?.toLocaleString() || '0'}</span>
                                            </div>
                                            <div className="stat">
                                                <span className="stat-label">CTR</span>
                                                <span className="stat-value">{campaign.ctr || '0%'}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="campaign-actions">
                                        {campaign.status === 'draft' && (
                                            <>
                                                <button
                                                    className="action-btn"
                                                    onClick={() => publishImmediately(campaign.id)}
                                                    disabled={loading}
                                                >
                                                    Publish
                                                </button>
                                                <button className="action-btn">Edit</button>
                                            </>
                                        )}
                                        {campaign.status === 'published' && (
                                            <button
                                                className="action-btn boost"
                                                onClick={() => boostCampaign(campaign.id)}
                                                disabled={loading}
                                            >
                                                 Boost
                                            </button>
                                        )}
                                        <button className="action-btn">Analytics</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
                <div className="analytics-section">
                    <h3> Campaign Analytics</h3>
                    <div className="analytics-grid">
                        <div className="analytics-card">
                            <div className="analytics-header">
                                <span className="analytics-icon"></span>
                                <span className="analytics-title">Total Reach</span>
                            </div>
                            <div className="analytics-value">{analytics.totalReach.toLocaleString()}</div>
                            <div className="analytics-trend"> 12% from last week</div>
                        </div>

                        <div className="analytics-card">
                            <div className="analytics-header">
                                <span className="analytics-icon"></span>
                                <span className="analytics-title">Engagements</span>
                            </div>
                            <div className="analytics-value">{analytics.engagements.toLocaleString()}</div>
                            <div className="analytics-trend"> 8% from last week</div>
                        </div>

                        <div className="analytics-card">
                            <div className="analytics-header">
                                <span className="analytics-icon"></span>
                                <span className="analytics-title">Link Clicks</span>
                            </div>
                            <div className="analytics-value">{analytics.clicks.toLocaleString()}</div>
                            <div className="analytics-trend"> 15% from last week</div>
                        </div>

                        <div className="analytics-card">
                            <div className="analytics-header">
                                <span className="analytics-icon"></span>
                                <span className="analytics-title">ROI</span>
                            </div>
                            <div className="analytics-value">{analytics.roi}</div>
                            <div className="analytics-trend"> 3.2% from last week</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SocialCampaignManager;
