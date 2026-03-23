/**
 * SecurityControlPanel.jsx
 * Security control panel
 * Comprehensive Security Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'security_bot';

// ==================== TAB COMPONENTS ====================

// Tab 1: Security Dashboard
const SecurityDashboardTab = ({ panelData, onAction }) => {
    const security = panelData?.security || {};

    return (
        <div className="space-y-6">
            {/* Security Score */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="relative">
                            <svg className="w-32 h-32 transform -rotate-90">
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none" className="text-gray-200 dark:text-gray-700" />
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none"
                                    className={`${security.score >= 80 ? 'text-green-500' : security.score >= 60 ? 'text-yellow-500' : 'text-red-500'}`}
                                    strokeDasharray={`${(security.score || 87) * 3.52} 352`} />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="text-center">
                                    <span className="text-3xl font-bold text-gray-900 dark:text-white">{security.score || 87}</span>
                                    <span className="block text-sm text-gray-500">/ 100</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Security Score</h3>
                            <p className="text-green-600 font-medium">Status: {security.status || 'Good'}</p>
                            <p className="text-sm text-gray-500 mt-1">Last scan: {security.lastScan || '10 minutes ago'}</p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={() => onAction('run_security_scan', {})}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2"
                        >
                            <span></span> Run Full Scan
                        </button>
                        <button
                            onClick={() => onAction('generate_security_report', {})}
                            className="px-6 py-3 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg font-medium flex items-center gap-2"
                        >
                            <span></span> Generate Report
                        </button>
                    </div>
                </div>
            </div>

            {/* Security Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{security.threatsBlocked || 156}</p>
                    <p className="text-sm text-green-100">Threats Blocked</p>
                    <p className="text-xs text-green-200 mt-1">Last 24 hours</p>
                </div>
                <div className="bg-gradient-to-br from-yellow-500 to-amber-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{security.warnings || 12}</p>
                    <p className="text-sm text-yellow-100">Active Warnings</p>
                    <p className="text-xs text-yellow-200 mt-1">{security.criticalWarnings || 3} critical</p>
                </div>
                <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{security.activeUsers || 45}</p>
                    <p className="text-sm text-blue-100">Active Sessions</p>
                    <p className="text-xs text-blue-200 mt-1">{security.suspiciousActivity || 2} suspicious</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{security.uptime || '99.9%'}</p>
                    <p className="text-sm text-purple-100">System Uptime</p>
                    <p className="text-xs text-purple-200 mt-1">Last 30 days</p>
                </div>
            </div>

            {/* Recent Security Events */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Security Events
                </h3>

                <div className="space-y-3">
                    {(panelData?.events || [
                        { type: 'blocked', message: 'Failed login attempt from IP 192.168.1.100', time: '2 min ago', severity: 'high' },
                        { type: 'warning', message: 'Unusual API activity detected', time: '15 min ago', severity: 'medium' },
                        { type: 'info', message: 'SSL certificate renewed successfully', time: '1 hour ago', severity: 'low' },
                        { type: 'blocked', message: 'SQL injection attempt blocked', time: '2 hours ago', severity: 'critical' },
                        { type: 'info', message: 'Security scan completed - no issues found', time: '3 hours ago', severity: 'info' }
                    ]).map((event, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border-l-4 ${event.severity === 'critical' ? 'bg-red-50 dark:bg-red-900/20 border-red-500' :
                            event.severity === 'high' ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-500' :
                                event.severity === 'medium' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                                    'bg-gray-50 dark:bg-gray-700 border-gray-400'
                            }`}>
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                    <span className="text-xl">
                                        {event.type === 'blocked' ? '' : event.type === 'warning' ? '' : ''}
                                    </span>
                                    <div>
                                        <p className="font-medium text-gray-900 dark:text-white">{event.message}</p>
                                        <p className="text-sm text-gray-500">{event.time}</p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs rounded ${event.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                    event.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                                        event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                    }`}>
                                    {event.severity}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 2: Access Control
const AccessControlTab = ({ panelData, onAction }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const users = panelData?.users || [];

    const filteredUsers = users.filter(u =>
        u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="space-y-6">
            {/* Access Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">{panelData?.accessStats?.totalUsers || 128}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.accessStats?.activeNow || 45}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Active Now</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{panelData?.accessStats?.suspended || 3}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Suspended</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-red-600">{panelData?.accessStats?.locked || 5}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Locked Accounts</p>
                </div>
            </div>

            {/* User Management */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        User Access Management
                    </h3>

                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search users..."
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                        <button
                            onClick={() => onAction('add_user', {})}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                        >
                            Add User
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Active</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">2FA</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(filteredUsers.length > 0 ? filteredUsers : [
                                { id: 1, name: 'John Doe', email: 'john@gts.com', role: 'Admin', status: 'Active', lastActive: '5 min ago', twoFa: true },
                                { id: 2, name: 'Jane Smith', email: 'jane@gts.com', role: 'Manager', status: 'Active', lastActive: '10 min ago', twoFa: true },
                                { id: 3, name: 'Bob Wilson', email: 'bob@gts.com', role: 'User', status: 'Suspended', lastActive: '2 days ago', twoFa: false },
                                { id: 4, name: 'Alice Brown', email: 'alice@gts.com', role: 'User', status: 'Active', lastActive: '1 hour ago', twoFa: true }
                            ]).map((user, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                                                {user.name?.charAt(0) || 'U'}
                                            </div>
                                            <div>
                                                <p className="font-medium text-gray-900 dark:text-white">{user.name}</p>
                                                <p className="text-sm text-gray-500">{user.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${user.role === 'Admin' ? 'bg-purple-100 text-purple-800' :
                                            user.role === 'Manager' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${user.status === 'Active' ? 'bg-green-100 text-green-800' :
                                            user.status === 'Suspended' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {user.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{user.lastActive}</td>
                                    <td className="px-4 py-3">
                                        <span className={`text-lg ${user.twoFa ? 'text-green-500' : 'text-gray-400'}`}>
                                            {user.twoFa ? '' : ''}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => onAction('edit_user', { userId: user.id })}
                                                className="text-blue-600 hover:text-blue-800 text-sm"
                                            >
                                                Edit
                                            </button>
                                            <button
                                                onClick={() => onAction('reset_password', { userId: user.id })}
                                                className="text-yellow-600 hover:text-yellow-800 text-sm"
                                            >
                                                Reset
                                            </button>
                                            {user.status === 'Active' ? (
                                                <button
                                                    onClick={() => onAction('suspend_user', { userId: user.id })}
                                                    className="text-red-600 hover:text-red-800 text-sm"
                                                >
                                                    Suspend
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => onAction('activate_user', { userId: user.id })}
                                                    className="text-green-600 hover:text-green-800 text-sm"
                                                >
                                                    Activate
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Role Management */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Role Permissions
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { role: 'Admin', permissions: ['Full Access', 'User Management', 'System Config', 'Security Settings'], color: 'purple' },
                        { role: 'Manager', permissions: ['Read/Write Data', 'View Reports', 'Manage Team', 'Limited Config'], color: 'blue' },
                        { role: 'User', permissions: ['Read Data', 'Create Records', 'View Own Reports'], color: 'gray' }
                    ].map((role, idx) => (
                        <div key={idx} className={`p-4 border-2 border-${role.color}-200 dark:border-${role.color}-800 rounded-lg`}>
                            <div className="flex items-center justify-between mb-3">
                                <h4 className={`font-bold text-${role.color}-600`}>{role.role}</h4>
                                <button className="text-sm text-blue-600 hover:text-blue-800">Edit</button>
                            </div>
                            <ul className="space-y-2">
                                {role.permissions.map((perm, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                        <span className="text-green-500"></span>
                                        {perm}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 3: Threat Detection
const ThreatDetectionTab = ({ panelData, onAction }) => {
    const threats = panelData?.threats || [];

    return (
        <div className="space-y-6">
            {/* Threat Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-red-500 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.threatStats?.critical || 2}</p>
                    <p className="text-sm text-red-100">Critical Threats</p>
                </div>
                <div className="bg-orange-500 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.threatStats?.high || 8}</p>
                    <p className="text-sm text-orange-100">High Priority</p>
                </div>
                <div className="bg-yellow-500 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.threatStats?.medium || 15}</p>
                    <p className="text-sm text-yellow-100">Medium Priority</p>
                </div>
                <div className="bg-green-500 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.threatStats?.resolved || 156}</p>
                    <p className="text-sm text-green-100">Resolved (24h)</p>
                </div>
            </div>

            {/* Active Threats */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Active Threats
                    </h3>
                    <button
                        onClick={() => onAction('scan_threats', {})}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium"
                    >
                        Scan Now
                    </button>
                </div>

                <div className="space-y-4">
                    {(threats.length > 0 ? threats : [
                        { id: 'THR-001', type: 'Brute Force Attack', source: '192.168.1.100', target: 'Login API', severity: 'critical', detected: '5 min ago', status: 'active' },
                        { id: 'THR-002', type: 'SQL Injection', source: '10.0.0.50', target: '/api/search', severity: 'high', detected: '15 min ago', status: 'blocked' },
                        { id: 'THR-003', type: 'Suspicious Login', source: 'Unknown Location', target: 'User: admin@gts.com', severity: 'medium', detected: '1 hour ago', status: 'monitoring' },
                        { id: 'THR-004', type: 'Port Scan', source: '203.0.113.50', target: 'Server Ports', severity: 'low', detected: '2 hours ago', status: 'blocked' }
                    ]).map((threat, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border-l-4 ${threat.severity === 'critical' ? 'bg-red-50 dark:bg-red-900/20 border-red-500' :
                            threat.severity === 'high' ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-500' :
                                threat.severity === 'medium' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                                    'bg-gray-50 dark:bg-gray-700 border-gray-400'
                            }`}>
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-gray-900 dark:text-white">{threat.type}</span>
                                        <span className={`px-2 py-0.5 text-xs rounded ${threat.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                            threat.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                                                threat.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-gray-100 text-gray-800'
                                            }`}>
                                            {threat.severity}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                        Source: {threat.source}  Target: {threat.target}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">Detected: {threat.detected}</p>
                                </div>

                                <div className="flex items-center gap-3">
                                    <span className={`px-3 py-1 text-xs rounded-full ${threat.status === 'active' ? 'bg-red-100 text-red-800' :
                                        threat.status === 'blocked' ? 'bg-green-100 text-green-800' :
                                            'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {threat.status}
                                    </span>

                                    {threat.status === 'active' && (
                                        <button
                                            onClick={() => onAction('block_threat', { threatId: threat.id })}
                                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
                                        >
                                            Block
                                        </button>
                                    )}
                                    <button
                                        onClick={() => onAction('investigate_threat', { threatId: threat.id })}
                                        className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                    >
                                        Investigate
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* IP Blacklist */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    IP Blacklist
                </h3>

                <div className="flex flex-wrap gap-2 mb-4">
                    {['192.168.1.100', '10.0.0.50', '203.0.113.50', '198.51.100.25'].map((ip, idx) => (
                        <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm flex items-center gap-2">
                            {ip}
                            <button className="hover:text-red-600"></button>
                        </span>
                    ))}
                </div>

                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Add IP to blacklist..."
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <button
                        onClick={() => onAction('add_to_blacklist', {})}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
                    >
                        Add to Blacklist
                    </button>
                </div>
            </div>
        </div>
    );
};

// Tab 4: Audit Logs
const AuditLogsTab = ({ panelData, onAction }) => {
    const [filter, setFilter] = useState('all');
    const logs = panelData?.auditLogs || [];

    return (
        <div className="space-y-6">
            {/* Log Filters */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap items-center gap-4">
                    <span className="font-medium text-gray-700 dark:text-gray-300">Filter:</span>
                    {['all', 'login', 'data_access', 'config_change', 'security'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === f
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                }`}
                        >
                            {f.replace('_', ' ').charAt(0).toUpperCase() + f.replace('_', ' ').slice(1)}
                        </button>
                    ))}

                    <div className="ml-auto flex gap-2">
                        <button
                            onClick={() => onAction('export_logs', {})}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm font-medium"
                        >
                            Export Logs
                        </button>
                    </div>
                </div>
            </div>

            {/* Audit Log Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Audit Trail
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(logs.length > 0 ? logs : [
                                { timestamp: '2025-01-15 14:30:22', user: 'admin@gts.com', action: 'Login', resource: 'Auth System', ip: '192.168.1.10', result: 'Success' },
                                { timestamp: '2025-01-15 14:28:15', user: 'john@gts.com', action: 'Data Export', resource: 'Loads Table', ip: '192.168.1.15', result: 'Success' },
                                { timestamp: '2025-01-15 14:25:00', user: 'unknown', action: 'Failed Login', resource: 'Auth System', ip: '10.0.0.50', result: 'Failed' },
                                { timestamp: '2025-01-15 14:20:30', user: 'admin@gts.com', action: 'Config Change', resource: 'Security Settings', ip: '192.168.1.10', result: 'Success' },
                                { timestamp: '2025-01-15 14:15:45', user: 'jane@gts.com', action: 'Create Record', resource: 'Customers', ip: '192.168.1.20', result: 'Success' }
                            ]).map((log, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{log.timestamp}</td>
                                    <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{log.user}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${log.action === 'Login' || log.action === 'Failed Login' ? 'bg-blue-100 text-blue-800' :
                                            log.action === 'Data Export' ? 'bg-purple-100 text-purple-800' :
                                                log.action === 'Config Change' ? 'bg-orange-100 text-orange-800' :
                                                    'bg-gray-100 text-gray-800'
                                            }`}>
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{log.resource}</td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{log.ip}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${log.result === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {log.result}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const SecurityControlPanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [panelData, setPanelData] = useState({});
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [actionLog, setActionLog] = useState([]);

    const fetchPanelData = useCallback(async () => {
        try {
            const response = await axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`);
            setPanelData(response.data || {});
            setConnected(true);
            setLastUpdate(new Date());
        } catch (error) {
            console.error('Failed to fetch panel data:', error);
            setConnected(false);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPanelData();
        const interval = setInterval(fetchPanelData, 15000); // More frequent for security
        return () => clearInterval(interval);
    }, [fetchPanelData]);

    const handleAction = async (action, params = {}) => {
        const logEntry = {
            id: Date.now(),
            action,
            params,
            timestamp: new Date().toISOString(),
            status: 'pending'
        };
        setActionLog(prev => [logEntry, ...prev.slice(0, 19)]);

        try {
            const response = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
                action,
                ...params
            });

            setActionLog(prev => prev.map(log =>
                log.id === logEntry.id ? { ...log, status: 'success', result: response.data } : log
            ));

            fetchPanelData();
            return response.data;
        } catch (error) {
            setActionLog(prev => prev.map(log =>
                log.id === logEntry.id ? { ...log, status: 'error', error: error.message } : log
            ));
            throw error;
        }
    };

    const tabs = [
        { id: 'dashboard', label: 'Security Dashboard', icon: '', component: SecurityDashboardTab },
        { id: 'access', label: 'Access Control', icon: '', component: AccessControlTab },
        { id: 'threats', label: 'Threat Detection', icon: '', component: ThreatDetectionTab },
        { id: 'audit', label: 'Audit Logs', icon: '', component: AuditLogsTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || SecurityDashboardTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Security Control Panel...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-gradient-to-br from-red-500 to-rose-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Security Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Security and protection system
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">{panelData?.stats?.score || 87}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Security Score</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-red-600">{panelData?.stats?.threats || 2}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Active Threats</p>
                                </div>
                            </div>

                            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></span>
                                <span className="text-sm font-medium">{connected ? 'Protected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex overflow-x-auto">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                                    ? 'border-red-600 text-red-600 bg-red-50 dark:bg-red-900/20'
                                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="text-xl">{tab.icon}</span>
                                <span className="font-medium">{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="lg:col-span-3">
                        <ActiveTabComponent panelData={panelData} onAction={handleAction} />
                    </div>

                    <div className="lg:col-span-1 space-y-6">
                        {/* Quick Actions */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Emergency Actions
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => handleAction('lockdown_system', {})}
                                    className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> System Lockdown
                                </button>
                                <button
                                    onClick={() => handleAction('force_logout_all', {})}
                                    className="w-full px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Force Logout All
                                </button>
                                <button
                                    onClick={() => handleAction('run_security_scan', {})}
                                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Full Security Scan
                                </button>
                                <button
                                    onClick={() => handleAction('backup_security_config', {})}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Backup Config
                                </button>
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Security Log
                            </h3>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {actionLog.length > 0 ? actionLog.slice(0, 5).map(log => (
                                    <div key={log.id} className="p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-gray-900 dark:text-white">{log.action}</span>
                                            <span className={`text-xs px-2 py-0.5 rounded ${log.status === 'success' ? 'bg-green-100 text-green-800' :
                                                log.status === 'error' ? 'bg-red-100 text-red-800' :
                                                    'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {log.status}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-1">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                )) : (
                                    <p className="text-sm text-gray-500 text-center py-4">No recent activity</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-6">
                <div className="max-w-7xl mx-auto px-4 py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <span>Security Control Panel v2.0</span>
                        <span>Last scan: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SecurityControlPanel;
