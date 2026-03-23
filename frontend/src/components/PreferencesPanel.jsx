import React, { useState, useEffect } from 'react';
import { Globe, Moon, Sun, Bell, Monitor, Save, RefreshCw, TestTube } from 'lucide-react';
import axiosClient from '../api/axiosClient';
import { useTranslation } from '../contexts/TranslationContext';
import notificationService from '../services/notificationService';

const PreferencesPanel = () => {
    const { t } = useTranslation();

    const [preferences, setPreferences] = useState({
        theme: 'dark',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        notifications: {
            email: true,
            push: true,
            sms: false,
            marketing: false
        },
        dashboard_layout: 'default'
    });

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        fetchPreferences();
    }, []);

    const fetchPreferences = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await axiosClient.get('/api/v1/users/me/preferences');
            if (response.data.ok) {
                const incoming = response.data.preferences || {};
                const safeTheme = incoming.theme === 'light' ? 'dark' : incoming.theme;
                setPreferences({
                    ...incoming,
                    theme: safeTheme || 'dark'
                });
            }
        } catch (err) {
            console.error('Failed to fetch preferences:', err);
            setError('Failed to load preferences');
        } finally {
            setLoading(false);
        }
    };

    const updatePreferences = async () => {
        try {
            setSaving(true);
            setError(null);
            setSuccess(false);

            const response = await axiosClient.put('/api/v1/users/me/preferences', preferences);
            if (response.data.ok) {
                setSuccess(true);
                setTimeout(() => setSuccess(false), 3000);
            }
        } catch (err) {
            console.error('Failed to update preferences:', err);
            setError('Failed to save preferences');
        } finally {
            setSaving(false);
        }
    };

    const handleNotificationChange = (type, value) => {
        setPreferences(prev => ({
            ...prev,
            notifications: {
                ...prev.notifications,
                [type]: value
            }
        }));
    };

    const testNotification = async (type) => {
        try {
            setError(null);
            const result = await notificationService.testNotification(type, 'test@example.com');
            setSuccess(`Test ${type} notification sent successfully!`);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            console.error(`Failed to test ${type} notification:`, err);
            setError(`Failed to test ${type} notification`);
        }
    };

    const setupPushNotifications = async () => {
        try {
            setError(null);
            await notificationService.setupPushNotifications();
            setSuccess('Push notifications enabled successfully!');
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            console.error('Failed to setup push notifications:', err);
            setError('Failed to enable push notifications. Please check your browser settings.');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-slate-400" />
                <span className="ml-2 text-slate-400">Loading preferences...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Language & Theme */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Globe className="w-5 h-5" />
                    Language & Appearance
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Theme
                        </label>
                        <select
                            value={preferences.theme}
                            onChange={(e) => {
                                const newTheme = e.target.value;
                                setPreferences(prev => ({ ...prev, theme: newTheme }));

                                // Apply theme immediately
                                if (newTheme === 'auto') {
                                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                                    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'dark');
                                } else {
                                    document.documentElement.setAttribute('data-theme', newTheme);
                                }
                            }}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="dark">{t('theme.dark', 'Dark')}</option>
                            <option value="auto">{t('theme.auto', 'Auto')}</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Timezone */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Timezone</h3>
                <div className="max-w-md">
                    <select
                        value={preferences.timezone}
                        onChange={(e) => setPreferences(prev => ({ ...prev, timezone: e.target.value }))}
                        className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">Eastern Time</option>
                        <option value="America/Chicago">Central Time</option>
                        <option value="America/Denver">Mountain Time</option>
                        <option value="America/Los_Angeles">Pacific Time</option>
                        <option value="Europe/London">London</option>
                        <option value="Europe/Paris">Paris</option>
                        <option value="Asia/Dubai">Dubai</option>
                        <option value="Asia/Riyadh">Riyadh</option>
                    </select>
                </div>
            </div>

            {/* Notifications */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Bell className="w-5 h-5" />
                    Notification Preferences
                </h3>

                <div className="space-y-4">
                    {/* Push Notification Setup */}
                    <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                        <div>
                            <p className="text-white font-medium">Push Notification Setup</p>
                            <p className="text-slate-400 text-sm">Enable browser push notifications</p>
                        </div>
                        <button
                            onClick={setupPushNotifications}
                            className="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded text-sm transition-colors"
                        >
                            Enable
                        </button>
                    </div>

                    {Object.entries(preferences.notifications).map(([type, enabled]) => (
                        <div key={type} className="flex items-center justify-between">
                            <div className="flex-1">
                                <p className="text-white font-medium capitalize">
                                    {type === 'push' ? 'Push Notifications' : type === 'sms' ? 'SMS' : type}
                                </p>
                                <p className="text-slate-400 text-sm">
                                    {type === 'email' && 'Receive updates via email'}
                                    {type === 'push' && 'Receive push notifications in browser'}
                                    {type === 'sms' && 'Receive text messages'}
                                    {type === 'marketing' && 'Receive marketing communications'}
                                </p>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => testNotification(type)}
                                    disabled={!enabled}
                                    className="p-1 text-slate-400 hover:text-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
                                    title={`Test ${type} notification`}
                                >
                                    <TestTube className="w-4 h-4" />
                                </button>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={enabled}
                                        onChange={(e) => handleNotificationChange(type, e.target.checked)}
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                                </label>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Dashboard Layout */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Monitor className="w-5 h-5" />
                    Dashboard Layout
                </h3>

                <div className="max-w-md">
                    <select
                        value={preferences.dashboard_layout}
                        onChange={(e) => setPreferences(prev => ({ ...prev, dashboard_layout: e.target.value }))}
                        className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                        <option value="default">{t('dashboard.default', 'Default Layout')}</option>
                        <option value="compact">{t('dashboard.compact', 'Compact Layout')}</option>
                        <option value="detailed">{t('dashboard.detailed', 'Detailed Layout')}</option>
                        <option value="minimal">{t('dashboard.minimal', 'Minimal Layout')}</option>
                    </select>
                    <p className="text-slate-400 text-sm mt-1">
                        {preferences.dashboard_layout === 'default' && t('dashboard.default_desc', 'Balanced view with essential widgets')}
                        {preferences.dashboard_layout === 'compact' && t('dashboard.compact_desc', 'Space-efficient layout for quick overview')}
                        {preferences.dashboard_layout === 'detailed' && t('dashboard.detailed_desc', 'Comprehensive view with all available data')}
                        {preferences.dashboard_layout === 'minimal' && t('dashboard.minimal_desc', 'Minimal interface focusing on key metrics')}
                    </p>
                </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center gap-4">
                <button
                    onClick={updatePreferences}
                    disabled={saving}
                    className="flex items-center gap-2 px-6 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {saving ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                        <Save className="w-4 h-4" />
                    )}
                    {saving ? 'Saving...' : 'Save Preferences'}
                </button>

                {success && (
                    <span className="text-green-400 text-sm">Preferences saved successfully!</span>
                )}

                {error && (
                    <span className="text-red-400 text-sm">{error}</span>
                )}
            </div>
        </div>
    );
};

export default PreferencesPanel;
