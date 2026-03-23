import React, { useState, useEffect } from 'react';
import { Monitor, Smartphone, MapPin, Calendar, Shield, LogOut, RefreshCw, AlertTriangle } from 'lucide-react';
import axiosClient from '../api/axiosClient';

const SessionsPanel = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [revoking, setRevoking] = useState(null);

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await axiosClient.get('/api/v1/auth/sessions');
            if (response.data.ok) {
                setSessions(response.data.sessions);
            }
        } catch (err) {
            console.error('Failed to fetch sessions:', err);
            setError('Failed to load active sessions');
        } finally {
            setLoading(false);
        }
    };

    const revokeSession = async (sessionId) => {
        if (!confirm('Are you sure you want to revoke this session? You will be logged out from that device.')) {
            return;
        }

        try {
            setRevoking(sessionId);
            await axiosClient.delete(`/api/v1/auth/sessions/${sessionId}`);
            // Remove the session from the list
            setSessions(prev => prev.filter(session => session.id !== sessionId));
        } catch (err) {
            console.error('Failed to revoke session:', err);
            setError('Failed to revoke session');
        } finally {
            setRevoking(null);
        }
    };

    const getDeviceIcon = (deviceInfo) => {
        if (deviceInfo?.toLowerCase().includes('mobile')) {
            return <Smartphone className="w-5 h-5" />;
        }
        return <Monitor className="w-5 h-5" />;
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-slate-400" />
                <span className="ml-2 text-slate-400">Loading active sessions...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Active Sessions
                </h3>
                <p className="text-slate-400 text-sm">
                    Manage your active sessions across different devices and browsers.
                    Revoking a session will log you out from that device.
                </p>
            </div>

            {/* Security Notice */}
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
                    <div>
                        <h4 className="text-yellow-400 font-medium mb-1">Security Recommendation</h4>
                        <p className="text-yellow-200 text-sm">
                            Regularly review and revoke sessions from unfamiliar devices or locations.
                            If you suspect unauthorized access, change your password immediately.
                        </p>
                    </div>
                </div>
            </div>

            {/* Sessions List */}
            <div className="space-y-4">
                {sessions.length === 0 ? (
                    <div className="glass-card p-6 text-center">
                        <Shield className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                        <p className="text-slate-400">No active sessions found</p>
                    </div>
                ) : (
                    sessions.map((session) => (
                        <div key={session.id} className="glass-card p-6">
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4">
                                    <div className="p-3 bg-slate-800/50 rounded-lg">
                                        {getDeviceIcon(session.device_info)}
                                    </div>

                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h4 className="text-white font-medium">
                                                {session.device_info || 'Unknown Device'}
                                            </h4>
                                            {session.is_current_session && (
                                                <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                                                    Current Session
                                                </span>
                                            )}
                                        </div>

                                        <div className="space-y-1 text-sm text-slate-400">
                                            {session.location && (
                                                <div className="flex items-center gap-2">
                                                    <MapPin className="w-4 h-4" />
                                                    <span>{session.location}</span>
                                                </div>
                                            )}

                                            <div className="flex items-center gap-2">
                                                <Calendar className="w-4 h-4" />
                                                <span>Created: {formatDate(session.created_at)}</span>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <Calendar className="w-4 h-4" />
                                                <span>Expires: {formatDate(session.expires_at)}</span>
                                            </div>

                                            {session.ip_address && (
                                                <div className="flex items-center gap-2">
                                                    <Shield className="w-4 h-4" />
                                                    <span>IP: {session.ip_address}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-2">
                                    {!session.is_current_session && (
                                        <button
                                            onClick={() => revokeSession(session.id)}
                                            disabled={revoking === session.id}
                                            className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-400/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {revoking === session.id ? (
                                                <RefreshCw className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <LogOut className="w-4 h-4" />
                                            )}
                                            {revoking === session.id ? 'Revoking...' : 'Revoke'}
                                        </button>
                                    )}

                                    {session.is_current_session && (
                                        <span className="px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-400/30 rounded-lg text-sm text-center">
                                            Active
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <button
                    onClick={fetchSessions}
                    className="flex items-center gap-2 px-6 py-2 bg-slate-700/50 hover:bg-slate-700/70 text-slate-300 border border-slate-600 rounded-lg transition-colors"
                >
                    <RefreshCw className="w-4 h-4" />
                    Refresh Sessions
                </button>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                    <p className="text-red-400 text-sm">{error}</p>
                </div>
            )}
        </div>
    );
};

export default SessionsPanel;

