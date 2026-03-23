import React, { useState, useEffect } from 'react';
import axiosClient from "../../api/axiosClient";
import './SocialMediaDashboard.css';

const SocialMediaDashboard = () => {
    const [connectedAccounts, setConnectedAccounts] = useState([]);
    const [scheduledPosts, setScheduledPosts] = useState([]);
    const [analytics, setAnalytics] = useState({});
    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [accountsRes, postsRes, analyticsRes] = await Promise.all([
                axiosClient.get('/api/v1/admin/social-media/accounts'),
                axiosClient.get('/api/v1/admin/social-media/posts?status=scheduled'),
                axiosClient.get('/api/v1/admin/social-media/analytics/summary')
            ]);

            setConnectedAccounts(accountsRes.data.accounts || []);
            setScheduledPosts(postsRes.data.posts || []);
            setAnalytics(analyticsRes.data || {});
            setLoading(false);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            setError('Failed to load dashboard data');
            setLoading(false);
        }
    };

    const connectPlatform = async (platform) => {
        try {
            const response = await axiosClient.post(`/api/v1/admin/social-media/connect/${platform}`);
            if (response.data.auth_url) {
                window.open(response.data.auth_url, '_blank', 'width=600,height=600');
            }
        } catch (error) {
            console.error('Error connecting platform:', error);
            alert('Failed to connect platform');
        }
    };

    const disconnectPlatform = async (platform) => {
        if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return;

        try {
            await axiosClient.post(`/api/v1/admin/social-media/disconnect/${platform}`);
            fetchDashboardData();
        } catch (error) {
            console.error('Error disconnecting platform:', error);
            alert('Failed to disconnect platform');
        }
    };

    const syncPlatform = async (platform) => {
        try {
            await axiosClient.post(`/api/v1/admin/social-media/sync/${platform}`);
            fetchDashboardData();
        } catch (error) {
            console.error('Error syncing platform:', error);
            alert('Failed to sync platform');
        }
    };

    const renderPlatformCard = (account) => {
        const platformIcons = {
            linkedin: '💼',
            twitter: '🐦',
            facebook: '📘',
            instagram: '📸',
            youtube: '🎬'
        };

        return (
            <div key={account.id} className={`platform-card ${account.is_connected ? 'connected' : 'disconnected'}`}>
                <div className="platform-header">
                    <div className="platform-icon">
                        {platformIcons[account.platform] || '📱'}
                    </div>
                    <div className="platform-info">
                        <h4>{account.platform.charAt(0).toUpperCase() + account.platform.slice(1)}</h4>
                        <span className={`status-badge ${account.is_connected ? 'connected' : 'disconnected'}`}>
                            {account.is_connected ? '✅ Connected' : '❌ Not Connected'}
                        </span>
                    </div>
                    <div className="platform-actions">
                        {account.is_connected ? (
                            <>
                                <button
                                    className="btn-sync"
                                    onClick={() => syncPlatform(account.platform)}
                                    title="Sync data"
                                >
                                    🔄 Sync
                                </button>
                                <button
                                    className="btn-disconnect"
                                    onClick={() => disconnectPlatform(account.platform)}
                                >
                                    Disconnect
                                </button>
                            </>
                        ) : (
                            <button
                                className="btn-connect"
                                onClick={() => connectPlatform(account.platform)}
                            >
                                Connect Account
                            </button>
                        )}
                    </div>
                </div>

                {account.is_connected && (
                    <div className="platform-details">
                        <div className="account-info">
                            <p><strong>Account:</strong> {account.account_name || 'N/A'}</p>
                            <p><strong>Last Activity:</strong> {account.last_sync ? new Date(account.last_sync).toLocaleDateString() : 'Never'}</p>
                            <p><strong>Auto-posting:</strong> {account.auto_posting_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
                        </div>
                        <div className="platform-stats">
                            <div className="stat">
                                <span className="stat-value">{account.followers_count?.toLocaleString() || 0}</span>
                                <span className="stat-label">Followers</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">{account.posts_count || 0}</span>
                                <span className="stat-label">Total Posts</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const OverviewTab = () => (
        <div className="overview-tab">
            <div className="stats-grid">
                <div className="stat-card total">
                    <h3>Total Followers</h3>
                    <p className="stat-number">{analytics.totalFollowers?.toLocaleString() || 0}</p>
                    <span className="stat-change positive">+{analytics.followerGrowth || 0} this month</span>
                </div>
                <div className="stat-card engagement">
                    <h3>Engagement Rate</h3>
                    <p className="stat-number">{analytics.engagementRate || 0}%</p>
                    <span className="stat-change positive">+0.5% vs last month</span>
                </div>
                <div className="stat-card posts">
                    <h3>Posts This Month</h3>
                    <p className="stat-number">{analytics.monthlyPosts || 0}</p>
                    <span className="stat-change neutral">Target: 150</span>
                </div>
                <div className="stat-card reach">
                    <h3>Total Reach</h3>
                    <p className="stat-number">{analytics.totalReach?.toLocaleString() || 0}</p>
                    <span className="stat-change positive">+12% vs last month</span>
                </div>
            </div>

            <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="action-buttons">
                    <button className="action-btn" onClick={() => setActiveTab('scheduler')}>
                        📝 Create New Post
                    </button>
                    <button className="action-btn" onClick={() => setActiveTab('scheduler')}>
                        🗓️ Schedule Post
                    </button>
                    <button className="action-btn" onClick={() => setActiveTab('analytics')}>
                        📊 View Reports
                    </button>
                    <button className="action-btn" onClick={fetchDashboardData}>
                        🔄 Sync All Accounts
                    </button>
                </div>
            </div>

            <div className="recent-activity">
                <h3>Recent Activity</h3>
                <div className="activity-list">
                    {scheduledPosts.slice(0, 5).map(post => (
                        <div key={post.id} className="activity-item">
                            <span className="activity-icon">📝</span>
                            <div className="activity-details">
                                <p className="activity-title">{post.content?.substring(0, 60)}...</p>
                                <p className="activity-meta">
                                    Scheduled for {new Date(post.scheduled_time).toLocaleString()}
                                    on {post.platforms?.join(', ')}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const AccountsTab = () => (
        <div className="accounts-tab">
            <div className="accounts-header">
                <h3>Connected Accounts</h3>
                <button className="btn-add-account" onClick={() => setActiveTab('settings')}>
                    + Add New Platform
                </button>
            </div>

            <div className="platforms-grid">
                {connectedAccounts.map(account => renderPlatformCard(account))}
            </div>

            <div className="integration-guide">
                <h4>How to Connect:</h4>
                <ol>
                    <li>Click "Connect Account" next to the desired platform</li>
                    <li>A new window will open for authorization</li>
                    <li>Log in and approve the permissions</li>
                    <li>You'll be automatically redirected and the account will be linked</li>
                </ol>
            </div>
        </div>
    );

    const SchedulerTab = () => (
        <div className="scheduler-tab">
            <PostScheduler onPostCreated={fetchDashboardData} />
        </div>
    );

    const AnalyticsTab = () => (
        <div className="analytics-tab">
            <SocialAnalytics />
        </div>
    );

    const SettingsTab = () => (
        <div className="settings-tab">
            <SocialMediaSettings onSettingsUpdated={fetchDashboardData} />
        </div>
    );

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="error-container">
                <p className="error-message">❌ {error}</p>
                <button onClick={fetchDashboardData}>Retry</button>
            </div>
        );
    }

    return (
        <div className="social-media-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <h1>Social Media Command Center</h1>
                <p>Manage and track all social media accounts from one place</p>
            </div>

            {/* Tabs Navigation */}
            <div className="tabs-navigation">
                <button
                    className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    📊 Overview
                </button>
                <button
                    className={`tab-btn ${activeTab === 'accounts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('accounts')}
                >
                    🔗 Connected Accounts
                </button>
                <button
                    className={`tab-btn ${activeTab === 'scheduler' ? 'active' : ''}`}
                    onClick={() => setActiveTab('scheduler')}
                >
                    🗓️ Post Scheduler
                </button>
                <button
                    className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('analytics')}
                >
                    📈 Analytics
                </button>
                <button
                    className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
                    onClick={() => setActiveTab('settings')}
                >
                    ⚙️ Settings
                </button>
            </div>

            {/* Content based on active tab */}
            <div className="tab-content">
                {activeTab === 'overview' && <OverviewTab />}
                {activeTab === 'accounts' && <AccountsTab />}
                {activeTab === 'scheduler' && <SchedulerTab />}
                {activeTab === 'analytics' && <AnalyticsTab />}
                {activeTab === 'settings' && <SettingsTab />}
            </div>
        </div>
    );
};

// Post Scheduler Component
const PostScheduler = ({ onPostCreated }) => {
    const [content, setContent] = useState('');
    const [platforms, setPlatforms] = useState([]);
    const [scheduleTime, setScheduleTime] = useState('');
    const [link, setLink] = useState('');
    const [hashtags, setHashtags] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            await axiosClient.post('/api/v1/admin/social-media/posts', {
                content,
                platforms,
                scheduled_time: scheduleTime,
                link,
                hashtags: hashtags.split(' ').filter(h => h.startsWith('#'))
            });

            alert('Post scheduled successfully!');
            setContent('');
            setPlatforms([]);
            setScheduleTime('');
            setLink('');
            setHashtags('');
            onPostCreated();
        } catch (error) {
            console.error('Error scheduling post:', error);
            alert('Failed to schedule post');
        }
    };

    return (
        <div className="post-scheduler">
            <h3>Schedule New Post</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Content *</label>
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="What do you want to share?"
                        rows={5}
                        required
                    />
                    <span className="char-count">{content.length}/280</span>
                </div>

                <div className="form-group">
                    <label>Platforms *</label>
                    <div className="platform-checkboxes">
                        {['linkedin', 'twitter', 'facebook'].map(platform => (
                            <label key={platform}>
                                <input
                                    type="checkbox"
                                    checked={platforms.includes(platform)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setPlatforms([...platforms, platform]);
                                        } else {
                                            setPlatforms(platforms.filter(p => p !== platform));
                                        }
                                    }}
                                />
                                {platform.charAt(0).toUpperCase() + platform.slice(1)}
                            </label>
                        ))}
                    </div>
                </div>

                <div className="form-group">
                    <label>Schedule Time</label>
                    <input
                        type="datetime-local"
                        value={scheduleTime}
                        onChange={(e) => setScheduleTime(e.target.value)}
                        min={new Date().toISOString().slice(0, 16)}
                    />
                    <small>Leave empty to post immediately</small>
                </div>

                <div className="form-group">
                    <label>Link (optional)</label>
                    <input
                        type="url"
                        value={link}
                        onChange={(e) => setLink(e.target.value)}
                        placeholder="https://example.com"
                    />
                </div>

                <div className="form-group">
                    <label>Hashtags (optional)</label>
                    <input
                        type="text"
                        value={hashtags}
                        onChange={(e) => setHashtags(e.target.value)}
                        placeholder="#logistics #freight #supplychain"
                    />
                </div>

                <button type="submit" className="btn-submit" disabled={!content || platforms.length === 0}>
                    {scheduleTime ? '🗓️ Schedule Post' : '📝 Post Now'}
                </button>
            </form>
        </div>
    );
};

// Analytics Component
const SocialAnalytics = () => {
    const [analyticsData, setAnalyticsData] = useState(null);
    const [selectedPlatform, setSelectedPlatform] = useState('all');

    useEffect(() => {
        fetchAnalytics();
    }, [selectedPlatform]);

    const fetchAnalytics = async () => {
        try {
            const response = await axiosClient.get(`/api/v1/admin/social-media/analytics/${selectedPlatform}`);
            setAnalyticsData(response.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    if (!analyticsData) {
        return <div>Loading analytics...</div>;
    }

    return (
        <div className="social-analytics">
            <h3>Performance Analytics</h3>
            <div className="platform-selector">
                {['all', 'linkedin', 'twitter', 'facebook'].map(platform => (
                    <button
                        key={platform}
                        className={selectedPlatform === platform ? 'active' : ''}
                        onClick={() => setSelectedPlatform(platform)}
                    >
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </button>
                ))}
            </div>
            <div className="analytics-content">
                <p>Analytics data for {selectedPlatform}</p>
                {/* Add charts and metrics here */}
            </div>
        </div>
    );
};

// Settings Component
const SocialMediaSettings = ({ onSettingsUpdated }) => {
    const [autoPostingEnabled, setAutoPostingEnabled] = useState(false);

    const handleSaveSettings = async () => {
        try {
            await axiosClient.post('/api/v1/admin/social-media/settings', {
                auto_posting_enabled: autoPostingEnabled
            });
            alert('Settings saved successfully!');
            onSettingsUpdated();
        } catch (error) {
            console.error('Error saving settings:', error);
            alert('Failed to save settings');
        }
    };

    return (
        <div className="social-settings">
            <h3>Social Media Settings</h3>
            <div className="setting-item">
                <label>
                    <input
                        type="checkbox"
                        checked={autoPostingEnabled}
                        onChange={(e) => setAutoPostingEnabled(e.target.checked)}
                    />
                    Enable auto-posting for new content
                </label>
            </div>
            <button onClick={handleSaveSettings} className="btn-save">
                Save Settings
            </button>
        </div>
    );
};

export default SocialMediaDashboard;
