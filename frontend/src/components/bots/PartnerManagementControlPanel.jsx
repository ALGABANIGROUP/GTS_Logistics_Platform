/**
 * PartnerManagementControlPanel.jsx
 * Partnership management system
 * Partner Management Intelligence Control Panel
 * Manages carrier partnerships and business relationships
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'partner_management';
const BACKEND_ACTIVE = true; // Backend integration enabled

// ==================== TAB COMPONENTS ====================

// Tab 1: Partner Dashboard
const PartnerDashboardTab = ({ panelData, onAction }) => {
    const stats = panelData?.stats || {};

    return (
        <div className="space-y-6">
            {/* Key Partner Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{stats.totalPartners || 248}</p>
                    <p className="text-sm text-blue-100">Total Partners</p>
                    <p className="text-xs text-blue-200 mt-1">+12 this month</p>
                </div>
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{stats.activeCarriers || 186}</p>
                    <p className="text-sm text-green-100">Active Carriers</p>
                    <p className="text-xs text-green-200 mt-1">92% engagement rate</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{stats.preferredPartners || 45}</p>
                    <p className="text-sm text-purple-100">Preferred Partners</p>
                    <p className="text-xs text-purple-200 mt-1">Top tier relationships</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-amber-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${stats.monthlyVolume || '2.4M'}</p>
                    <p className="text-sm text-orange-100">Monthly Volume</p>
                    <p className="text-xs text-orange-200 mt-1"> 18% vs last month</p>
                </div>
            </div>

            {/* Partner Health Overview */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                    <span className="text-2xl"></span>
                    Partnership Health Score
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[
                        { metric: 'On-Time Performance', score: 94, trend: '+2%', color: 'green' },
                        { metric: 'Claims Ratio', score: 98, trend: '+1%', color: 'green' },
                        { metric: 'Communication', score: 89, trend: '-1%', color: 'yellow' },
                        { metric: 'Payment History', score: 96, trend: '0%', color: 'green' }
                    ].map((item, idx) => (
                        <div key={idx} className="rounded-lg border border-white/5 bg-slate-900/50 p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-slate-300">{item.metric}</span>
                                <span className={`text-xs ${item.trend.startsWith('+') ? 'text-emerald-400' : item.trend.startsWith('-') ? 'text-rose-400' : 'text-slate-400'}`}>
                                    {item.trend}
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 overflow-hidden rounded-full bg-white/10">
                                    <div
                                        className={`h-full rounded-full ${item.score >= 90 ? 'bg-green-500' : item.score >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                                            }`}
                                        style={{ width: `${item.score}%` }}
                                    />
                                </div>
                                <span className="text-lg font-bold text-white">{item.score}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Partner Distribution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* By Type */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                    <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                        <span className="text-2xl"></span>
                        Partners by Type
                    </h3>
                    <div className="space-y-3">
                        {[
                            { type: 'Owner Operators', count: 124, percent: 50, color: 'blue' },
                            { type: 'Small Fleets (2-10)', count: 68, percent: 27, color: 'green' },
                            { type: 'Medium Fleets (11-50)', count: 38, percent: 15, color: 'purple' },
                            { type: 'Large Carriers (50+)', count: 18, percent: 8, color: 'orange' }
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                                <span className="flex-1 text-sm text-slate-200">{item.type}</span>
                                <span className="text-sm font-medium text-white">{item.count}</span>
                                <span className="w-12 text-right text-xs text-slate-400">{item.percent}%</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* By Region */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                    <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                        <span className="text-2xl"></span>
                        Partners by Region
                    </h3>
                    <div className="space-y-3">
                        {[
                            { region: 'Midwest', count: 78, percent: 31, color: 'blue' },
                            { region: 'Southeast', count: 62, percent: 25, color: 'green' },
                            { region: 'Southwest', count: 48, percent: 19, color: 'purple' },
                            { region: 'Northeast', count: 35, percent: 14, color: 'orange' },
                            { region: 'West Coast', count: 25, percent: 11, color: 'pink' }
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                                <span className="flex-1 text-sm text-slate-200">{item.region}</span>
                                <span className="text-sm font-medium text-white">{item.count}</span>
                                <span className="w-12 text-right text-xs text-slate-400">{item.percent}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Partner Activity */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                    <span className="text-2xl"></span>
                    Recent Partner Activity
                </h3>

                <div className="space-y-3">
                    {[
                        { action: 'New carrier onboarded', partner: 'Swift Logistics LLC', time: '2 hours ago', icon: '', type: 'success' },
                        { action: 'Contract renewed', partner: 'Prime Transport Inc', time: '5 hours ago', icon: '', type: 'success' },
                        { action: 'Performance review completed', partner: 'Eagle Carriers', time: '1 day ago', icon: '', type: 'info' },
                        { action: 'Insurance updated', partner: 'Midwest Trucking Co', time: '1 day ago', icon: '', type: 'success' },
                        { action: 'Tier upgraded to Preferred', partner: 'FastHaul Express', time: '2 days ago', icon: '', type: 'success' }
                    ].map((activity, idx) => (
                        <div key={idx} className={`flex items-center gap-4 rounded-lg border p-3 ${activity.type === 'success' ? 'border-emerald-500/20 bg-emerald-500/10' :
                            activity.type === 'warning' ? 'border-amber-500/20 bg-amber-500/10' :
                                'border-white/5 bg-slate-900/50'
                            }`}>
                            <span className="text-2xl">{activity.icon}</span>
                            <div className="flex-1">
                                <p className="font-medium text-white">{activity.action}</p>
                                <p className="text-sm text-slate-300">{activity.partner}</p>
                            </div>
                            <span className="text-xs text-slate-400">{activity.time}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 2: Carrier Directory
const CarrierDirectoryTab = ({ panelData, onAction }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [filterTier, setFilterTier] = useState('all');
    const [filterStatus, setFilterStatus] = useState('all');

    const carriers = panelData?.carriers || [];

    const filteredCarriers = carriers.filter(c => {
        const matchesSearch = c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            c.mc.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesTier = filterTier === 'all' || c.tier.toLowerCase() === filterTier;
        const matchesStatus = filterStatus === 'all' || c.status.toLowerCase() === filterStatus;
        return matchesSearch && matchesTier && matchesStatus;
    });

    return (
        <div className="space-y-6">
            {/* Search and Filters */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/30 backdrop-blur-xl">
                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex-1 min-w-64">
                        <input
                            type="text"
                            placeholder="Search by name, MC#, DOT#..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full rounded-lg border border-white/10 bg-slate-950/70 px-4 py-2 text-white"
                        />
                    </div>
                    <select
                        value={filterTier}
                        onChange={(e) => setFilterTier(e.target.value)}
                        className="rounded-lg border border-white/10 bg-slate-950/70 px-4 py-2 text-white"
                    >
                        <option value="all">All Tiers</option>
                        <option value="preferred">Preferred</option>
                        <option value="standard">Standard</option>
                        <option value="new">New</option>
                    </select>
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="rounded-lg border border-white/10 bg-slate-950/70 px-4 py-2 text-white"
                    >
                        <option value="all">All Status</option>
                        <option value="active">Active</option>
                        <option value="pending">Pending</option>
                        <option value="inactive">Inactive</option>
                    </select>
                    <button
                        onClick={() => onAction('add_carrier', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                    >
                        + Add Carrier
                    </button>
                </div>
            </div>

            {/* Carrier List */}
            <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-slate-950/80">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Carrier</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MC / DOT</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loads (YTD)</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Region</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {filteredCarriers.map((carrier, idx) => (
                                <tr key={idx} className="hover:bg-white/5">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 font-bold">
                                                {carrier.name.charAt(0)}
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">{carrier.name}</p>
                                                <p className="text-xs text-gray-500">{carrier.id}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <p className="text-sm text-white">{carrier.mc}</p>
                                        <p className="text-xs text-gray-500">{carrier.dot}</p>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded-full ${carrier.tier === 'Preferred' ? 'bg-purple-100 text-purple-800' :
                                            carrier.tier === 'Standard' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                            {carrier.tier === 'Preferred' && ' '}{carrier.tier}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${carrier.status === 'Active' ? 'bg-green-100 text-green-800' :
                                            carrier.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {carrier.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm font-medium text-white">
                                        {carrier.loads}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1">
                                            <span className="text-yellow-500"></span>
                                            <span className="text-sm font-medium text-white">
                                                {carrier.rating || 'N/A'}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-slate-300">
                                        {carrier.region}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => onAction('view_carrier', { carrierId: carrier.id })}
                                                className="text-blue-600 hover:text-blue-800 text-sm"
                                            >
                                                View
                                            </button>
                                            <button
                                                onClick={() => onAction('edit_carrier', { carrierId: carrier.id })}
                                                className="text-gray-600 hover:text-gray-800 text-sm"
                                            >
                                                Edit
                                            </button>
                                        </div>
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

// Tab 3: Relationship Management
const RelationshipManagementTab = ({ panelData, onAction }) => {
    return (
        <div className="space-y-6">
            {/* Relationship Tiers */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                    { tier: 'Preferred Partners', count: 45, color: 'purple', icon: '', benefits: ['Priority load assignment', 'Premium rates', 'Dedicated support'] },
                    { tier: 'Standard Partners', count: 156, color: 'blue', icon: '', benefits: ['Regular load access', 'Standard rates', 'Email support'] },
                    { tier: 'New Partners', count: 47, color: 'green', icon: '', benefits: ['Onboarding support', 'Trial period', 'Performance tracking'] }
                ].map((item, idx) => (
                    <div key={idx} className={`bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 border-${item.color}-200 dark:border-${item.color}-800`}>
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <span className="text-2xl">{item.icon}</span>
                                <h3 className="font-bold text-gray-900 dark:text-white">{item.tier}</h3>
                            </div>
                            <span className={`text-2xl font-bold text-${item.color}-600`}>{item.count}</span>
                        </div>
                        <ul className="space-y-2">
                            {item.benefits.map((benefit, bidx) => (
                                <li key={bidx} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                    <span className="text-green-500"></span>
                                    {benefit}
                                </li>
                            ))}
                        </ul>
                        <button
                            onClick={() => onAction('view_tier_partners', { tier: item.tier })}
                            className={`mt-4 w-full py-2 border border-${item.color}-300 hover:bg-${item.color}-50 dark:hover:bg-${item.color}-900/20 rounded-lg text-sm font-medium`}
                        >
                            View Partners
                        </button>
                    </div>
                ))}
            </div>

            {/* Partner Engagement */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Partner Engagement Metrics
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[
                        { metric: 'Avg Response Time', value: '12 min', change: '-18%', positive: true },
                        { metric: 'Load Acceptance Rate', value: '78%', change: '+5%', positive: true },
                        { metric: 'Communication Score', value: '4.6/5', change: '+0.2', positive: true },
                        { metric: 'Partner Churn Rate', value: '2.3%', change: '-0.5%', positive: true }
                    ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-center">
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">{item.value}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{item.metric}</p>
                            <p className={`text-xs mt-1 ${item.positive ? 'text-green-600' : 'text-red-600'}`}>
                                {item.change}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Upcoming Reviews */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Upcoming Partner Reviews
                    </h3>
                    <button
                        onClick={() => onAction('schedule_review', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                    >
                        Schedule Review
                    </button>
                </div>

                <div className="space-y-3">
                    {[
                        { partner: 'Swift Logistics LLC', type: 'Quarterly Review', date: 'Jan 15, 2026', status: 'Scheduled' },
                        { partner: 'Prime Transport Inc', type: 'Contract Renewal', date: 'Jan 20, 2026', status: 'Pending' },
                        { partner: 'Eagle Carriers', type: 'Performance Review', date: 'Jan 25, 2026', status: 'Scheduled' },
                        { partner: 'FastHaul Express', type: 'Tier Evaluation', date: 'Feb 1, 2026', status: 'Pending' }
                    ].map((review, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 font-bold">
                                    {review.partner.charAt(0)}
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900 dark:text-white">{review.partner}</p>
                                    <p className="text-sm text-gray-500">{review.type}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-gray-600 dark:text-gray-400">{review.date}</span>
                                <span className={`px-2 py-1 text-xs rounded ${review.status === 'Scheduled' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                    }`}>
                                    {review.status}
                                </span>
                                <button
                                    onClick={() => onAction('view_review', { partner: review.partner })}
                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                >
                                    Details
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Communication Center */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Communication Center
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                        onClick={() => onAction('send_broadcast', {})}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md hover:border-blue-500 transition-all text-left"
                    >
                        <span className="text-2xl block mb-2"></span>
                        <h4 className="font-medium text-gray-900 dark:text-white">Send Broadcast</h4>
                        <p className="text-sm text-gray-500">Notify all or selected partners</p>
                    </button>
                    <button
                        onClick={() => onAction('view_conversations', {})}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md hover:border-blue-500 transition-all text-left"
                    >
                        <span className="text-2xl block mb-2"></span>
                        <h4 className="font-medium text-gray-900 dark:text-white">Conversations</h4>
                        <p className="text-sm text-gray-500">View partner messages</p>
                    </button>
                    <button
                        onClick={() => onAction('manage_templates', {})}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md hover:border-blue-500 transition-all text-left"
                    >
                        <span className="text-2xl block mb-2"></span>
                        <h4 className="font-medium text-gray-900 dark:text-white">Templates</h4>
                        <p className="text-sm text-gray-500">Manage message templates</p>
                    </button>
                </div>
            </div>
        </div>
    );
};

// Tab 4: Onboarding & Compliance
const OnboardingComplianceTab = ({ panelData, onAction }) => {
    return (
        <div className="space-y-6">
            {/* Onboarding Pipeline */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Onboarding Pipeline
                    </h3>
                    <button
                        onClick={() => onAction('start_onboarding', {})}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium"
                    >
                        + New Carrier
                    </button>
                </div>

                <div className="flex flex-wrap gap-4 mb-6">
                    {[
                        { stage: 'Application', count: 8, color: 'gray' },
                        { stage: 'Documentation', count: 5, color: 'blue' },
                        { stage: 'Verification', count: 3, color: 'yellow' },
                        { stage: 'Approval', count: 2, color: 'purple' },
                        { stage: 'Complete', count: 12, color: 'green' }
                    ].map((stage, idx) => (
                        <div key={idx} className="flex-1 min-w-32">
                            <div className={`rounded-lg border p-4 text-center ${
                                stage.color === 'green'
                                    ? 'border-emerald-500/20 bg-emerald-500/10'
                                    : stage.color === 'blue'
                                        ? 'border-blue-500/20 bg-blue-500/10'
                                        : stage.color === 'yellow'
                                            ? 'border-amber-500/20 bg-amber-500/10'
                                            : stage.color === 'purple'
                                                ? 'border-violet-500/20 bg-violet-500/10'
                                                : 'border-white/10 bg-slate-900/50'
                            }`}>
                                <p className={`text-2xl font-bold text-${stage.color}-600`}>{stage.count}</p>
                                <p className="text-sm text-slate-300">{stage.stage}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Pending Onboarding */}
                <div className="space-y-3">
                    {[
                        { carrier: 'Continental Freight', stage: 'Documentation', progress: 40, submitted: 'Jan 3, 2026', missing: ['W-9', 'Insurance'] },
                        { carrier: 'Mountain Express', stage: 'Verification', progress: 70, submitted: 'Jan 1, 2026', missing: ['FMCSA Check'] },
                        { carrier: 'Valley Trucking', stage: 'Application', progress: 20, submitted: 'Jan 4, 2026', missing: ['MC Authority', 'W-9', 'COI'] }
                    ].map((item, idx) => (
                        <div key={idx} className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-full border border-blue-500/20 bg-blue-500/10 font-bold text-blue-300">
                                        {item.carrier.charAt(0)}
                                    </div>
                                    <div>
                                        <p className="font-medium text-white">{item.carrier}</p>
                                        <p className="text-xs text-slate-400">Submitted: {item.submitted}</p>
                                    </div>
                                </div>
                                <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-200">{item.stage}</span>
                            </div>

                            <div className="flex items-center gap-2 mb-2">
                                <div className="flex-1 h-2 overflow-hidden rounded-full bg-white/10">
                                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${item.progress}%` }} />
                                </div>
                                <span className="text-sm font-medium text-slate-300">{item.progress}%</span>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex flex-wrap gap-1">
                                    {item.missing.map((doc, didx) => (
                                        <span key={didx} className="rounded border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-xs text-rose-200">
                                            Missing: {doc}
                                        </span>
                                    ))}
                                </div>
                                <button
                                    onClick={() => onAction('continue_onboarding', { carrier: item.carrier })}
                                    className="text-sm font-medium text-blue-300 hover:text-blue-200"
                                >
                                    Continue
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Compliance Status */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                    <span className="text-2xl"></span>
                    Partner Compliance Status
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {[
                        { label: 'Fully Compliant', count: 215, percent: 87, color: 'green' },
                        { label: 'Expiring Soon', count: 18, percent: 7, color: 'yellow' },
                        { label: 'Non-Compliant', count: 8, percent: 3, color: 'red' },
                        { label: 'Under Review', count: 7, percent: 3, color: 'blue' }
                    ].map((stat, idx) => (
                        <div key={idx} className={`rounded-lg border p-4 text-center ${
                            stat.color === 'green'
                                ? 'border-emerald-500/20 bg-emerald-500/10'
                                : stat.color === 'yellow'
                                    ? 'border-amber-500/20 bg-amber-500/10'
                                    : stat.color === 'red'
                                        ? 'border-rose-500/20 bg-rose-500/10'
                                        : 'border-blue-500/20 bg-blue-500/10'
                        }`}>
                            <p className={`text-2xl font-bold text-${stat.color}-600`}>{stat.count}</p>
                            <p className="text-sm text-slate-300">{stat.label}</p>
                            <p className="text-xs text-slate-400">{stat.percent}%</p>
                        </div>
                    ))}
                </div>

                {/* Compliance Alerts */}
                <div className="space-y-2">
                    {[
                        { carrier: 'Valley Express', issue: 'Insurance expiring in 15 days', priority: 'High' },
                        { carrier: 'Northern Haul', issue: 'MC Authority renewal needed', priority: 'Medium' },
                        { carrier: 'Coast to Coast', issue: 'W-9 update required', priority: 'Low' }
                    ].map((alert, idx) => (
                        <div key={idx} className={`flex items-center justify-between rounded-lg border p-3 ${alert.priority === 'High' ? 'border-rose-500/20 bg-rose-500/10' :
                            alert.priority === 'Medium' ? 'border-amber-500/20 bg-amber-500/10' :
                                'border-white/10 bg-slate-900/50'
                            }`}>
                            <div className="flex items-center gap-3">
                                <span className={`rounded px-2 py-0.5 text-xs ${alert.priority === 'High' ? 'bg-rose-500/15 text-rose-200' :
                                    alert.priority === 'Medium' ? 'bg-amber-500/15 text-amber-200' :
                                        'bg-slate-800 text-slate-300'
                                    }`}>
                                    {alert.priority}
                                </span>
                                <span className="font-medium text-white">{alert.carrier}</span>
                                <span className="text-sm text-slate-300">{alert.issue}</span>
                            </div>
                            <button
                                onClick={() => onAction('resolve_compliance', { carrier: alert.carrier })}
                                className="text-sm text-blue-300 hover:text-blue-200"
                            >
                                Resolve
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Required Documents */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/30 backdrop-blur-xl">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
                    <span className="text-2xl"></span>
                    Required Documents Checklist
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {[
                        { doc: 'MC Authority', required: true },
                        { doc: 'DOT Number', required: true },
                        { doc: 'Certificate of Insurance', required: true },
                        { doc: 'W-9 Form', required: true },
                        { doc: 'Carrier Agreement', required: true },
                        { doc: 'Rate Confirmation Template', required: false },
                        { doc: 'Safety Rating', required: false },
                        { doc: 'Equipment List', required: false }
                    ].map((doc, idx) => (
                        <div key={idx} className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/50 p-3">
                            <span className={`text-xl ${doc.required ? 'text-rose-400' : 'text-slate-500'}`}>
                                {doc.required ? '' : ''}
                            </span>
                            <span className="text-sm text-white">{doc.doc}</span>
                            {doc.required && <span className="text-xs text-rose-300">Required</span>}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const PartnerManagementControlPanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [panelData, setPanelData] = useState({});
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [actionLog, setActionLog] = useState([]);

    const fetchPanelData = useCallback(async () => {
        setLoading(true);

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
        const interval = setInterval(fetchPanelData, 30000);
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
        { id: 'dashboard', label: 'Partner Dashboard', icon: '', component: PartnerDashboardTab },
        { id: 'directory', label: 'Carrier Directory', icon: '', component: CarrierDirectoryTab },
        { id: 'relationships', label: 'Relationships', icon: '', component: RelationshipManagementTab },
        { id: 'onboarding', label: 'Onboarding', icon: '', component: OnboardingComplianceTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || PartnerDashboardTab;

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-950">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Partner Management...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950">
            {/* Header */}
            <div className="border-b border-white/10 bg-slate-950/80 shadow-lg shadow-black/30 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-white">
                                    Partner Management
                                </h1>
                                <p className="text-sm text-slate-300">
                                    Partnership management and carrier relationships
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-4">
                                <div className="rounded-lg border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-center">
                                    <p className="text-xl font-bold text-blue-600">{panelData?.stats?.totalPartners || 0}</p>
                                    <p className="text-xs text-slate-300">Partners</p>
                                </div>
                                <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-center">
                                    <p className="text-xl font-bold text-green-600">{panelData?.stats?.activeCarriers || 0}</p>
                                    <p className="text-xs text-slate-300">Active</p>
                                </div>
                            </div>

                            <div className={`flex items-center gap-2 rounded-lg px-3 py-2 ${connected ? 'border border-emerald-500/20 bg-emerald-500/10 text-emerald-300' : 'border border-white/10 bg-white/5 text-slate-300'
                                }`}>
                                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></span>
                                <span className="text-sm font-medium">{connected ? 'Connected' : 'Offline'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex overflow-x-auto">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                                    ? 'border-blue-500 text-blue-300 bg-blue-500/10'
                                    : 'border-transparent text-slate-400 hover:text-white hover:bg-white/5'
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
                        <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/30 backdrop-blur-xl">
                            <h3 className="mb-4 flex items-center gap-2 font-bold text-white">
                                <span></span> Quick Actions
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => handleAction('add_carrier', {})}
                                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Add New Carrier
                                </button>
                                <button
                                    onClick={() => handleAction('search_carriers', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Search Partners
                                </button>
                                <button
                                    onClick={() => handleAction('send_broadcast', {})}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Send Broadcast
                                </button>
                                <button
                                    onClick={() => handleAction('export_directory', {})}
                                    className="flex w-full items-center justify-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-white/5"
                                >
                                    <span></span> Export Directory
                                </button>
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/30 backdrop-blur-xl">
                            <h3 className="mb-4 flex items-center gap-2 font-bold text-white">
                                <span></span> Activity Log
                            </h3>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {actionLog.length > 0 ? actionLog.slice(0, 5).map(log => (
                                    <div key={log.id} className="rounded border border-white/5 bg-slate-900/50 p-2 text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-white">{log.action}</span>
                                            <span className={`text-xs px-2 py-0.5 rounded ${log.status === 'success' ? 'bg-green-100 text-green-800' :
                                                log.status === 'error' ? 'bg-red-100 text-red-800' :
                                                    log.status === 'offline' ? 'bg-gray-100 text-gray-800' :
                                                        'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {log.status}
                                            </span>
                                        </div>
                                        <p className="mt-1 text-xs text-slate-400">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                )) : (
                                    <p className="py-4 text-center text-sm text-slate-400">No recent activity</p>
                                )}
                            </div>
                        </div>

                        {/* Partner Alerts */}
                        <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/30 backdrop-blur-xl">
                            <h3 className="mb-4 flex items-center gap-2 font-bold text-white">
                                <span></span> Alerts
                            </h3>
                            <div className="space-y-2">
                                <div className="rounded border border-amber-500/20 bg-amber-500/10 p-2 text-sm">
                                    <p className="text-amber-200">3 carriers need insurance renewal</p>
                                </div>
                                <div className="rounded border border-blue-500/20 bg-blue-500/10 p-2 text-sm">
                                    <p className="text-blue-200">8 pending onboarding applications</p>
                                </div>
                                <div className="rounded border border-emerald-500/20 bg-emerald-500/10 p-2 text-sm">
                                    <p className="text-emerald-200">12 carriers onboarded this month</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-6 border-t border-white/10 bg-slate-950/70 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-slate-400">
                        <span>Partner Management Control Panel v1.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PartnerManagementControlPanel;
