/**
 * SalesControlPanel.jsx
 * Sales intelligence control panel
 * Comprehensive Sales Intelligence Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'sales_intelligence';

// ==================== TAB COMPONENTS ====================

// Tab 1: Sales Dashboard
const SalesDashboardTab = ({ panelData, onAction }) => {
    const sales = panelData?.sales || {};

    return (
        <div className="space-y-6">
            {/* Key Sales Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${sales.revenue?.toLocaleString() || '1.5M'}</p>
                    <p className="text-sm text-blue-100">Monthly Revenue</p>
                    <p className="text-xs text-blue-200 mt-1"> 18% vs last month</p>
                </div>
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{sales.deals || 47}</p>
                    <p className="text-sm text-green-100">Closed Deals</p>
                    <p className="text-xs text-green-200 mt-1"> 12 this week</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{sales.conversion || '32%'}</p>
                    <p className="text-sm text-purple-100">Conversion Rate</p>
                    <p className="text-xs text-purple-200 mt-1"> 5% improvement</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-amber-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${sales.avgDeal?.toLocaleString() || '32K'}</p>
                    <p className="text-sm text-orange-100">Avg Deal Size</p>
                    <p className="text-xs text-orange-200 mt-1"> 8% increase</p>
                </div>
            </div>

            {/* Sales Pipeline */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Sales Pipeline
                </h3>

                <div className="flex flex-wrap items-center justify-between gap-4">
                    {[
                        { stage: 'Lead', count: sales.pipeline?.lead || 85, value: '$425K', color: 'gray' },
                        { stage: 'Qualified', count: sales.pipeline?.qualified || 42, value: '$315K', color: 'blue' },
                        { stage: 'Proposal', count: sales.pipeline?.proposal || 28, value: '$280K', color: 'yellow' },
                        { stage: 'Negotiation', count: sales.pipeline?.negotiation || 15, value: '$195K', color: 'orange' },
                        { stage: 'Closed Won', count: sales.pipeline?.won || 47, value: '$1.5M', color: 'green' }
                    ].map((stage, idx) => (
                        <div key={idx} className="flex-1 min-w-[150px] text-center">
                            <div className={`h-2 bg-${stage.color}-500 rounded-full mb-2`}></div>
                            <p className="font-bold text-gray-900 dark:text-white">{stage.count}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{stage.stage}</p>
                            <p className={`text-xs text-${stage.color}-600 font-medium`}>{stage.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Activities */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Sales Activities
                </h3>

                <div className="space-y-3">
                    {(panelData?.activities || [
                        { type: 'deal_closed', message: 'Closed deal with ABC Corp - $45,000', time: '30 min ago', icon: '' },
                        { type: 'proposal_sent', message: 'Proposal sent to XYZ Logistics', time: '1 hour ago', icon: '' },
                        { type: 'meeting', message: 'Call scheduled with Global Trade', time: '2 hours ago', icon: '' },
                        { type: 'lead', message: 'New lead: FastShip Inc - High Priority', time: '3 hours ago', icon: '' },
                        { type: 'follow_up', message: 'Follow-up completed with Prime Carriers', time: '4 hours ago', icon: '' }
                    ]).map((activity, idx) => (
                        <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <span className="text-2xl">{activity.icon}</span>
                            <div className="flex-1">
                                <p className="text-gray-900 dark:text-white">{activity.message}</p>
                                <p className="text-sm text-gray-500">{activity.time}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Team Performance */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Team Performance
                </h3>

                <div className="space-y-4">
                    {(panelData?.teamPerformance || [
                        { name: 'Sarah Johnson', deals: 15, revenue: '$485K', quota: 95 },
                        { name: 'Mike Chen', deals: 12, revenue: '$380K', quota: 88 },
                        { name: 'Emily Davis', deals: 10, revenue: '$320K', quota: 78 },
                        { name: 'John Smith', deals: 8, revenue: '$260K', quota: 65 }
                    ]).map((member, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                                    {member.name.charAt(0)}
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900 dark:text-white">{member.name}</p>
                                    <p className="text-sm text-gray-500">{member.deals} deals  {member.revenue}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className={`text-lg font-bold ${member.quota >= 80 ? 'text-green-600' : member.quota >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                                    {member.quota}%
                                </p>
                                <p className="text-xs text-gray-500">of quota</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 2: Lead Management
const LeadManagementTab = ({ panelData, onAction }) => {
    const [newLead, setNewLead] = useState({
        company: '',
        contact: '',
        email: '',
        phone: '',
        source: 'Website',
        priority: 'Medium'
    });

    const leads = panelData?.leads || [];

    const handleAddLead = () => {
        if (newLead.company && newLead.contact) {
            onAction('add_lead', newLead);
            setNewLead({ company: '', contact: '', email: '', phone: '', source: 'Website', priority: 'Medium' });
        }
    };

    return (
        <div className="space-y-6">
            {/* Lead Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">{panelData?.leadStats?.total || 245}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Leads</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.leadStats?.new || 38}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">New This Week</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{panelData?.leadStats?.qualified || 85}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Qualified</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-red-600">{panelData?.leadStats?.hot || 15}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Hot Leads</p>
                </div>
            </div>

            {/* Add New Lead */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Add New Lead
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
                        <input
                            type="text"
                            value={newLead.company}
                            onChange={(e) => setNewLead({ ...newLead, company: e.target.value })}
                            placeholder="Company name"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contact Name</label>
                        <input
                            type="text"
                            value={newLead.contact}
                            onChange={(e) => setNewLead({ ...newLead, contact: e.target.value })}
                            placeholder="Contact person"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            value={newLead.email}
                            onChange={(e) => setNewLead({ ...newLead, email: e.target.value })}
                            placeholder="email@company.com"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
                        <input
                            type="tel"
                            value={newLead.phone}
                            onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })}
                            placeholder="+1 (555) 000-0000"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Source</label>
                        <select
                            value={newLead.source}
                            onChange={(e) => setNewLead({ ...newLead, source: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="Website">Website</option>
                            <option value="Referral">Referral</option>
                            <option value="Trade Show">Trade Show</option>
                            <option value="Cold Call">Cold Call</option>
                            <option value="LinkedIn">LinkedIn</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
                        <select
                            value={newLead.priority}
                            onChange={(e) => setNewLead({ ...newLead, priority: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                            <option value="Hot">Hot </option>
                        </select>
                    </div>
                </div>

                <button
                    onClick={handleAddLead}
                    className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                >
                    Add Lead
                </button>
            </div>

            {/* Lead List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Lead Pipeline
                    </h3>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onAction('import_leads', {})}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm font-medium"
                        >
                            Import
                        </button>
                        <button
                            onClick={() => onAction('export_leads', {})}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm font-medium"
                        >
                            Export
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(leads.length > 0 ? leads : [
                                { id: 1, company: 'ABC Logistics', contact: 'John Doe', email: 'john@abc.com', status: 'Qualified', priority: 'Hot', value: 85000 },
                                { id: 2, company: 'XYZ Transport', contact: 'Jane Smith', email: 'jane@xyz.com', status: 'New', priority: 'High', value: 45000 },
                                { id: 3, company: 'Global Freight', contact: 'Bob Wilson', email: 'bob@global.com', status: 'Proposal', priority: 'Medium', value: 62000 },
                                { id: 4, company: 'FastShip Inc', contact: 'Alice Brown', email: 'alice@fast.com', status: 'Negotiation', priority: 'High', value: 120000 }
                            ]).map((lead, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3">
                                        <p className="font-medium text-gray-900 dark:text-white">{lead.company}</p>
                                    </td>
                                    <td className="px-4 py-3">
                                        <p className="text-sm text-gray-900 dark:text-white">{lead.contact}</p>
                                        <p className="text-xs text-gray-500">{lead.email}</p>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${lead.status === 'New' ? 'bg-blue-100 text-blue-800' :
                                            lead.status === 'Qualified' ? 'bg-green-100 text-green-800' :
                                                lead.status === 'Proposal' ? 'bg-yellow-100 text-yellow-800' :
                                                    lead.status === 'Negotiation' ? 'bg-orange-100 text-orange-800' :
                                                        'bg-gray-100 text-gray-800'
                                            }`}>
                                            {lead.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${lead.priority === 'Hot' ? 'bg-red-100 text-red-800' :
                                            lead.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                                                lead.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-gray-100 text-gray-800'
                                            }`}>
                                            {lead.priority} {lead.priority === 'Hot' && ''}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 font-medium text-green-600">
                                        ${lead.value?.toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => onAction('contact_lead', { leadId: lead.id })}
                                                className="text-blue-600 hover:text-blue-800 text-sm"
                                            >
                                                Contact
                                            </button>
                                            <button
                                                onClick={() => onAction('view_lead', { leadId: lead.id })}
                                                className="text-gray-600 hover:text-gray-800 text-sm"
                                            >
                                                View
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

// Tab 3: Campaign Management
const CampaignManagementTab = ({ panelData, onAction }) => {
    const campaigns = panelData?.campaigns || [];

    return (
        <div className="space-y-6">
            {/* Campaign Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">{panelData?.campaignStats?.active || 5}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Active Campaigns</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.campaignStats?.emailsSent || '12.5K'}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Emails Sent</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-purple-600">{panelData?.campaignStats?.openRate || '28%'}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Open Rate</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-orange-600">{panelData?.campaignStats?.conversions || 156}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Conversions</p>
                </div>
            </div>

            {/* Active Campaigns */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Active Campaigns
                    </h3>
                    <button
                        onClick={() => onAction('create_campaign', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                    >
                        New Campaign
                    </button>
                </div>

                <div className="space-y-4">
                    {(campaigns.length > 0 ? campaigns : [
                        { id: 1, name: 'Q1 Freight Services', type: 'Email', status: 'Active', sent: 2500, opens: 680, clicks: 145, conversions: 28 },
                        { id: 2, name: 'New Customer Welcome', type: 'Drip', status: 'Active', sent: 850, opens: 425, clicks: 98, conversions: 15 },
                        { id: 3, name: 'Rate Increase Notice', type: 'Email', status: 'Scheduled', sent: 0, opens: 0, clicks: 0, conversions: 0 },
                        { id: 4, name: 'Holiday Promotions', type: 'Multi-channel', status: 'Completed', sent: 5200, opens: 1820, clicks: 456, conversions: 89 }
                    ]).map((campaign, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <h4 className="font-bold text-gray-900 dark:text-white">{campaign.name}</h4>
                                        <span className={`px-2 py-0.5 text-xs rounded ${campaign.status === 'Active' ? 'bg-green-100 text-green-800' :
                                            campaign.status === 'Scheduled' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                            {campaign.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">Type: {campaign.type}</p>
                                </div>

                                <div className="flex items-center gap-6">
                                    <div className="text-center">
                                        <p className="font-bold text-gray-900 dark:text-white">{campaign.sent?.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">Sent</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="font-bold text-blue-600">{campaign.opens?.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">Opens</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="font-bold text-purple-600">{campaign.clicks?.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">Clicks</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="font-bold text-green-600">{campaign.conversions}</p>
                                        <p className="text-xs text-gray-500">Conversions</p>
                                    </div>

                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onAction('view_campaign', { campaignId: campaign.id })}
                                            className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                        >
                                            View
                                        </button>
                                        {campaign.status === 'Active' && (
                                            <button
                                                onClick={() => onAction('pause_campaign', { campaignId: campaign.id })}
                                                className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded"
                                            >
                                                Pause
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Email Templates */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Email Templates
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { name: 'Welcome Email', category: 'Onboarding', usage: 245 },
                        { name: 'Rate Quote', category: 'Sales', usage: 1280 },
                        { name: 'Follow-up', category: 'Sales', usage: 890 },
                        { name: 'Proposal', category: 'Sales', usage: 456 },
                        { name: 'Thank You', category: 'Post-Sale', usage: 320 },
                        { name: 'Newsletter', category: 'Marketing', usage: 5200 }
                    ].map((template, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow cursor-pointer">
                            <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-gray-900 dark:text-white">{template.name}</h4>
                                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">{template.category}</span>
                            </div>
                            <p className="text-sm text-gray-500">{template.usage} times used</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 4: Sales Analytics
const SalesAnalyticsTab = ({ panelData, onAction }) => {
    return (
        <div className="space-y-6">
            {/* Revenue Analytics */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Revenue Analytics
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { period: 'This Month', revenue: '$485,200', growth: '+18%', trend: 'up' },
                        { period: 'This Quarter', revenue: '$1,245,800', growth: '+22%', trend: 'up' },
                        { period: 'Year to Date', revenue: '$4,850,000', growth: '+35%', trend: 'up' }
                    ].map((stat, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{stat.period}</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.revenue}</p>
                            <p className={`text-sm font-medium ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                                {stat.trend === 'up' ? '' : ''} {stat.growth} vs last period
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Win/Loss Analysis */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Win/Loss Analysis
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Win Reasons</h4>
                        <div className="space-y-2">
                            {[
                                { reason: 'Competitive Pricing', count: 45, percent: 38 },
                                { reason: 'Service Quality', count: 32, percent: 27 },
                                { reason: 'Fast Response', count: 25, percent: 21 },
                                { reason: 'Relationships', count: 16, percent: 14 }
                            ].map((item, idx) => (
                                <div key={idx} className="flex items-center gap-3">
                                    <div className="flex-1">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-700 dark:text-gray-300">{item.reason}</span>
                                            <span className="text-gray-500">{item.count} ({item.percent}%)</span>
                                        </div>
                                        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                            <div className="bg-green-500 h-2 rounded-full" style={{ width: `${item.percent}%` }}></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Loss Reasons</h4>
                        <div className="space-y-2">
                            {[
                                { reason: 'Price Too High', count: 28, percent: 42 },
                                { reason: 'Competitor Offer', count: 18, percent: 27 },
                                { reason: 'No Response', count: 12, percent: 18 },
                                { reason: 'Timing', count: 9, percent: 13 }
                            ].map((item, idx) => (
                                <div key={idx} className="flex items-center gap-3">
                                    <div className="flex-1">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-700 dark:text-gray-300">{item.reason}</span>
                                            <span className="text-gray-500">{item.count} ({item.percent}%)</span>
                                        </div>
                                        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                            <div className="bg-red-500 h-2 rounded-full" style={{ width: `${item.percent}%` }}></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Sales Forecasting */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Sales Forecast
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    {[
                        { month: 'February', forecast: '$520K', confidence: '85%' },
                        { month: 'March', forecast: '$580K', confidence: '78%' },
                        { month: 'Q2 Total', forecast: '$1.8M', confidence: '72%' },
                        { month: 'Year End', forecast: '$6.2M', confidence: '65%' }
                    ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400">{item.month}</p>
                            <p className="text-xl font-bold text-blue-600">{item.forecast}</p>
                            <p className="text-xs text-gray-500">{item.confidence} confidence</p>
                        </div>
                    ))}
                </div>

                <button
                    onClick={() => onAction('generate_forecast', {})}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                >
                    Update Forecast
                </button>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const SalesControlPanel = () => {
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
        { id: 'dashboard', label: 'Sales Dashboard', icon: '', component: SalesDashboardTab },
        { id: 'leads', label: 'Lead Management', icon: '', component: LeadManagementTab },
        { id: 'campaigns', label: 'Campaigns', icon: '', component: CampaignManagementTab },
        { id: 'analytics', label: 'Analytics', icon: '', component: SalesAnalyticsTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || SalesDashboardTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Sales Control Panel...</p>
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
                            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Sales Intelligence Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Sales & CRM System
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">${panelData?.stats?.revenue?.toLocaleString() || '1.5M'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Revenue</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-blue-600">{panelData?.stats?.deals || 47}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Deals</p>
                                </div>
                            </div>

                            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></span>
                                <span className="text-sm font-medium">{connected ? 'Connected' : 'Disconnected'}</span>
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
                                    ? 'border-blue-600 text-blue-600 bg-blue-50 dark:bg-blue-900/20'
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
                                <span></span> Quick Actions
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => handleAction('add_lead', {})}
                                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Add New Lead
                                </button>
                                <button
                                    onClick={() => handleAction('send_follow_ups', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Send Follow-ups
                                </button>
                                <button
                                    onClick={() => handleAction('generate_quotes', {})}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Generate Quotes
                                </button>
                                <button
                                    onClick={() => handleAction('export_sales_data', {})}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Export Report
                                </button>
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Activity Log
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
                        <span>Sales Intelligence Control Panel v2.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SalesControlPanel;
