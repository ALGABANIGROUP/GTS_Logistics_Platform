import React, { useState, useEffect } from 'react';

const SocialMediaDashboard = () => {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoPostingEnabled, setAutoPostingEnabled] = useState(false);

    useEffect(() => {
        fetchSocialAccounts();
    }, []);

    const fetchSocialAccounts = async () => {
        try {
            const response = await fetch('/api/v1/admin/social-media/accounts');
            const data = await response.json();
            setAccounts(data.accounts || []);
            setAutoPostingEnabled(data.auto_posting_enabled || false);
        } catch (error) {
            console.error('Failed to fetch social accounts:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleAutoPosting = async () => {
        try {
            const response = await fetch('/api/v1/admin/social-media/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ auto_posting_enabled: !autoPostingEnabled })
            });
            if (response.ok) {
                setAutoPostingEnabled(!autoPostingEnabled);
            }
        } catch (error) {
            console.error('Failed to toggle auto-posting:', error);
        }
    };

    const connectAccount = async (platform) => {
        try {
            const response = await fetch(`/api/v1/admin/social-media/connect/${platform}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (data.auth_url) {
                window.location.href = data.auth_url;
            }
        } catch (error) {
            console.error(`Failed to connect ${platform}:`, error);
        }
    };

    const disconnectAccount = async (platform) => {
        try {
            await fetch(`/api/v1/admin/social-media/disconnect/${platform}`, {
                method: 'DELETE'
            });
            await fetchSocialAccounts();
        } catch (error) {
            console.error(`Failed to disconnect ${platform}:`, error);
        }
    };

    if (loading) {
        return <div className="text-center py-8">Loading...</div>;
    }

    return (
        <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-white">Social Media Management</h2>
                <div className="flex items-center gap-3">
                    <span className="text-gray-300 text-sm">Auto-posting:</span>
                    <button
                        onClick={toggleAutoPosting}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${autoPostingEnabled
                                ? 'bg-green-600 text-white hover:bg-green-700'
                                : 'bg-gray-600 text-gray-300 hover:bg-gray-700'
                            }`}
                    >
                        {autoPostingEnabled ? '✅ Enabled' : '❌ Disabled'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['twitter', 'linkedin', 'facebook', 'instagram', 'tiktok'].map(platform => {
                    const account = accounts.find(a => a.platform === platform);
                    const isConnected = account?.is_connected || false;

                    return (
                        <div key={platform} className="bg-white/5 rounded-lg p-4 border border-white/10">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-white font-semibold capitalize">{platform}</span>
                                <span className={`text-xs px-2 py-1 rounded-full ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {isConnected ? '✅ Connected' : '❌ Not Connected'}
                                </span>
                            </div>

                            {isConnected ? (
                                <div>
                                    <p className="text-gray-400 text-xs mb-2">@{account?.username || 'username'}</p>
                                    <button
                                        onClick={() => disconnectAccount(platform)}
                                        className="w-full py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition text-sm"
                                    >
                                        Disconnect
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={() => connectAccount(platform)}
                                    className="w-full py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition text-sm"
                                >
                                    Connect Account
                                </button>
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="mt-6 pt-4 border-t border-white/10">
                <h3 className="text-white font-semibold mb-2">Auto-posting Settings</h3>
                <div className="grid grid-cols-2 gap-3">
                    <label className="flex items-center gap-2 text-gray-300 text-sm">
                        <input type="checkbox" checked={true} disabled className="w-4 h-4" />
                        New Blog Posts
                    </label>
                    <label className="flex items-center gap-2 text-gray-300 text-sm">
                        <input type="checkbox" checked={true} disabled className="w-4 h-4" />
                        New Services
                    </label>
                    <label className="flex items-center gap-2 text-gray-300 text-sm">
                        <input type="checkbox" checked={false} disabled className="w-4 h-4" />
                        Promotional Content
                    </label>
                    <label className="flex items-center gap-2 text-gray-300 text-sm">
                        <input type="checkbox" checked={true} disabled className="w-4 h-4" />
                        Company Updates
                    </label>
                </div>
            </div>
        </div>
    );
};

export default SocialMediaDashboard;
                </div >
            </div >
        </div >
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
