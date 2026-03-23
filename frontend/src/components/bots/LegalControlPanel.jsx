/**
 * LegalControlPanel.jsx
 * Legal counsel control panel
 * Comprehensive Legal Counsel Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'legal_counsel';

// ==================== TAB COMPONENTS ====================

// Tab 1: Legal Dashboard
const LegalDashboardTab = ({ panelData, onAction }) => {
    const legal = panelData?.legal || {};

    return (
        <div className="space-y-6">
            {/* Key Legal Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{legal.activeContracts || 156}</p>
                    <p className="text-sm text-indigo-100">Active Contracts</p>
                    <p className="text-xs text-indigo-200 mt-1">{legal.pendingReview || 12} pending review</p>
                </div>
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{legal.compliant || '98%'}</p>
                    <p className="text-sm text-green-100">Compliance Rate</p>
                    <p className="text-xs text-green-200 mt-1">FMCSA & DOT compliant</p>
                </div>
                <div className="bg-gradient-to-br from-yellow-500 to-amber-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{legal.expiringContracts || 8}</p>
                    <p className="text-sm text-yellow-100">Expiring Soon</p>
                    <p className="text-xs text-yellow-200 mt-1">Within 30 days</p>
                </div>
                <div className="bg-gradient-to-br from-red-500 to-rose-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{legal.disputes || 3}</p>
                    <p className="text-sm text-red-100">Active Disputes</p>
                    <p className="text-xs text-red-200 mt-1">{legal.resolvedDisputes || 12} resolved MTD</p>
                </div>
            </div>

            {/* Compliance Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Compliance Status
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                        { area: 'FMCSA Registration', status: 'Compliant', expiry: 'Dec 2025', icon: '' },
                        { area: 'Insurance Coverage', status: 'Compliant', expiry: 'Jun 2025', icon: '' },
                        { area: 'DOT Authority', status: 'Compliant', expiry: 'Mar 2026', icon: '' },
                        { area: 'Broker Bond', status: 'Compliant', expiry: 'Sep 2025', icon: '' }
                    ].map((item, idx) => (
                        <div key={idx} className="p-4 border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-xl">{item.icon}</span>
                                <span className="font-medium text-gray-900 dark:text-white">{item.area}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">{item.status}</span>
                                <span className="text-xs text-gray-500">Expires: {item.expiry}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Legal Activity */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Legal Activity
                </h3>

                <div className="space-y-3">
                    {(panelData?.activities || [
                        { type: 'contract', message: 'Carrier agreement signed with Swift Transport', time: '1 hour ago', icon: '' },
                        { type: 'review', message: 'Rate confirmation template reviewed and approved', time: '3 hours ago', icon: '' },
                        { type: 'compliance', message: 'Q1 compliance audit completed successfully', time: '1 day ago', icon: '' },
                        { type: 'dispute', message: 'Claim #CLM-2024-089 resolved in our favor', time: '2 days ago', icon: '' },
                        { type: 'update', message: 'Terms of Service updated for 2025', time: '3 days ago', icon: '' }
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

            {/* Risk Assessment */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Legal Risk Assessment
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900 dark:text-white">Contract Risk</span>
                            <span className="text-green-600 font-bold">Low</span>
                        </div>
                        <p className="text-sm text-gray-500">All contracts reviewed and up to date</p>
                    </div>
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900 dark:text-white">Compliance Risk</span>
                            <span className="text-yellow-600 font-bold">Medium</span>
                        </div>
                        <p className="text-sm text-gray-500">2 licenses expiring within 60 days</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900 dark:text-white">Litigation Risk</span>
                            <span className="text-green-600 font-bold">Low</span>
                        </div>
                        <p className="text-sm text-gray-500">No pending litigation</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Tab 2: Contract Management
const ContractManagementTab = ({ panelData, onAction }) => {
    const [filter, setFilter] = useState('all');
    const contracts = panelData?.contracts || [];

    const filteredContracts = contracts.filter(c =>
        filter === 'all' || c.type?.toLowerCase() === filter
    );

    return (
        <div className="space-y-6">
            {/* Contract Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                    { label: 'All Contracts', count: panelData?.contractStats?.total || 156, filter: 'all', color: 'blue' },
                    { label: 'Carrier', count: panelData?.contractStats?.carrier || 85, filter: 'carrier', color: 'green' },
                    { label: 'Customer', count: panelData?.contractStats?.customer || 42, filter: 'customer', color: 'purple' },
                    { label: 'Vendor', count: panelData?.contractStats?.vendor || 18, filter: 'vendor', color: 'orange' },
                    { label: 'Expiring', count: panelData?.contractStats?.expiring || 8, filter: 'expiring', color: 'red' }
                ].map((stat, idx) => (
                    <button
                        key={idx}
                        onClick={() => setFilter(stat.filter)}
                        className={`p-4 rounded-xl text-center transition-all ${filter === stat.filter
                            ? `bg-${stat.color}-600 text-white shadow-lg`
                            : `bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md`
                            }`}
                    >
                        <p className={`text-2xl font-bold ${filter === stat.filter ? 'text-white' : `text-${stat.color}-600`}`}>
                            {stat.count}
                        </p>
                        <p className={`text-sm ${filter === stat.filter ? 'text-white/80' : 'text-gray-600 dark:text-gray-400'}`}>
                            {stat.label}
                        </p>
                    </button>
                ))}
            </div>

            {/* Contract List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Contract Repository
                    </h3>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onAction('create_contract', {})}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                        >
                            New Contract
                        </button>
                        <button
                            onClick={() => onAction('bulk_renew', {})}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm font-medium"
                        >
                            Bulk Renew
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contract ID</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Party</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expiry</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(filteredContracts.length > 0 ? filteredContracts : [
                                { id: 'CTR-001', party: 'Swift Transport', type: 'Carrier', value: 150000, status: 'Active', expiry: '2025-12-31' },
                                { id: 'CTR-002', party: 'ABC Logistics', type: 'Customer', value: 280000, status: 'Active', expiry: '2025-06-30' },
                                { id: 'CTR-003', party: 'Prime Carriers', type: 'Carrier', value: 95000, status: 'Pending', expiry: '2025-09-15' },
                                { id: 'CTR-004', party: 'Global Freight', type: 'Customer', value: 420000, status: 'Active', expiry: '2025-03-31' },
                                { id: 'CTR-005', party: 'Tech Supplies Inc', type: 'Vendor', value: 35000, status: 'Expiring', expiry: '2025-02-28' }
                            ]).map((contract, idx) => (
                                <tr key={idx} className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${contract.status === 'Expiring' ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''
                                    }`}>
                                    <td className="px-4 py-3 text-sm font-medium text-blue-600">{contract.id}</td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{contract.party}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${contract.type === 'Carrier' ? 'bg-green-100 text-green-800' :
                                            contract.type === 'Customer' ? 'bg-purple-100 text-purple-800' :
                                                'bg-orange-100 text-orange-800'
                                            }`}>
                                            {contract.type}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                                        ${contract.value?.toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${contract.status === 'Active' ? 'bg-green-100 text-green-800' :
                                            contract.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {contract.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{contract.expiry}</td>
                                    <td className="px-4 py-3">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => onAction('view_contract', { contractId: contract.id })}
                                                className="text-blue-600 hover:text-blue-800 text-sm"
                                            >
                                                View
                                            </button>
                                            <button
                                                onClick={() => onAction('renew_contract', { contractId: contract.id })}
                                                className="text-green-600 hover:text-green-800 text-sm"
                                            >
                                                Renew
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Contract Templates */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Contract Templates
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { name: 'Carrier Agreement', description: 'Standard carrier/broker agreement', icon: '' },
                        { name: 'Rate Confirmation', description: 'Load rate confirmation template', icon: '' },
                        { name: 'Customer Contract', description: 'Shipper service agreement', icon: '' },
                        { name: 'NDA', description: 'Non-disclosure agreement', icon: '' },
                        { name: 'Insurance Certificate', description: 'Certificate of insurance request', icon: '' },
                        { name: 'Vendor Agreement', description: 'Third-party vendor contract', icon: '' }
                    ].map((template, idx) => (
                        <button
                            key={idx}
                            onClick={() => onAction('use_template', { template: template.name })}
                            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md hover:border-blue-500 transition-all text-left"
                        >
                            <span className="text-2xl block mb-2">{template.icon}</span>
                            <h4 className="font-medium text-gray-900 dark:text-white">{template.name}</h4>
                            <p className="text-sm text-gray-500">{template.description}</p>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 3: Dispute Resolution
const DisputeResolutionTab = ({ panelData, onAction }) => {
    const disputes = panelData?.disputes || [];

    return (
        <div className="space-y-6">
            {/* Dispute Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-red-600">{panelData?.disputeStats?.active || 3}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Active Disputes</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{panelData?.disputeStats?.pending || 5}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Pending Review</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.disputeStats?.resolved || 28}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Resolved (YTD)</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">${panelData?.disputeStats?.totalValue?.toLocaleString() || '45,000'}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Value at Risk</p>
                </div>
            </div>

            {/* Active Disputes */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Active Disputes
                    </h3>
                    <button
                        onClick={() => onAction('create_dispute', {})}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium"
                    >
                        File New Dispute
                    </button>
                </div>

                <div className="space-y-4">
                    {(disputes.length > 0 ? disputes : [
                        { id: 'DSP-001', type: 'Cargo Damage', party: 'Swift Transport', value: 12500, filed: '2025-01-10', status: 'In Mediation', priority: 'High' },
                        { id: 'DSP-002', type: 'Payment Dispute', party: 'ABC Logistics', value: 8500, filed: '2025-01-05', status: 'Under Review', priority: 'Medium' },
                        { id: 'DSP-003', type: 'Delivery Delay', party: 'FastShip Inc', value: 24000, filed: '2024-12-28', status: 'Negotiation', priority: 'High' }
                    ]).map((dispute, idx) => (
                        <div key={idx} className={`p-4 border rounded-lg ${dispute.priority === 'High' ? 'border-red-300 bg-red-50 dark:bg-red-900/20' :
                            dispute.priority === 'Medium' ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20' :
                                'border-gray-200 dark:border-gray-700'
                            }`}>
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-gray-900 dark:text-white">{dispute.id}</span>
                                        <span className={`px-2 py-0.5 text-xs rounded ${dispute.priority === 'High' ? 'bg-red-100 text-red-800' :
                                            dispute.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                            {dispute.priority} Priority
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                        {dispute.type}  {dispute.party}
                                    </p>
                                    <p className="text-xs text-gray-500">Filed: {dispute.filed}</p>
                                </div>

                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <p className="text-xl font-bold text-red-600">${dispute.value?.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">At Risk</p>
                                    </div>

                                    <span className={`px-3 py-1 text-xs rounded-full ${dispute.status === 'In Mediation' ? 'bg-blue-100 text-blue-800' :
                                        dispute.status === 'Under Review' ? 'bg-yellow-100 text-yellow-800' :
                                            dispute.status === 'Negotiation' ? 'bg-purple-100 text-purple-800' :
                                                'bg-gray-100 text-gray-800'
                                        }`}>
                                        {dispute.status}
                                    </span>

                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onAction('view_dispute', { disputeId: dispute.id })}
                                            className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                        >
                                            View
                                        </button>
                                        <button
                                            onClick={() => onAction('update_dispute', { disputeId: dispute.id })}
                                            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                                        >
                                            Update
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Resolution Guidelines */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Resolution Process
                </h3>

                <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    {[
                        { step: 1, label: 'File Claim', icon: '' },
                        { step: 2, label: 'Review', icon: '' },
                        { step: 3, label: 'Negotiation', icon: '' },
                        { step: 4, label: 'Mediation', icon: '' },
                        { step: 5, label: 'Resolution', icon: '' }
                    ].map((step, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                            <div className="flex flex-col items-center">
                                <span className="text-2xl">{step.icon}</span>
                                <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                                    {step.step}
                                </div>
                                <span className="text-xs text-gray-600 dark:text-gray-400 mt-1">{step.label}</span>
                            </div>
                            {idx < 4 && <span className="text-gray-400 text-2xl"></span>}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 4: Compliance & Regulations
const ComplianceRegulationsTab = ({ panelData, onAction }) => {
    return (
        <div className="space-y-6">
            {/* Compliance Score */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="relative">
                            <svg className="w-32 h-32 transform -rotate-90">
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none" className="text-gray-200 dark:text-gray-700" />
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none"
                                    className="text-green-500"
                                    strokeDasharray={`${(panelData?.compliance?.score || 98) * 3.52} 352`} />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="text-center">
                                    <span className="text-3xl font-bold text-gray-900 dark:text-white">{panelData?.compliance?.score || 98}%</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Score</h3>
                            <p className="text-green-600 font-medium">Excellent Standing</p>
                            <p className="text-sm text-gray-500 mt-1">Last audit: {panelData?.compliance?.lastAudit || 'Jan 10, 2025'}</p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={() => onAction('run_compliance_check', {})}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                        >
                            Run Compliance Check
                        </button>
                    </div>
                </div>
            </div>

            {/* Regulatory Requirements */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Regulatory Requirements
                </h3>

                <div className="space-y-3">
                    {[
                        { requirement: 'FMCSA Motor Carrier Registration', status: 'Compliant', nextDue: 'Dec 2025', agency: 'FMCSA' },
                        { requirement: 'Broker Authority (MC Number)', status: 'Compliant', nextDue: 'Dec 2025', agency: 'FMCSA' },
                        { requirement: 'Surety Bond ($75,000)', status: 'Compliant', nextDue: 'Sep 2025', agency: 'BMC-84' },
                        { requirement: 'General Liability Insurance', status: 'Compliant', nextDue: 'Jun 2025', agency: 'Insurance' },
                        { requirement: 'Cargo Insurance', status: 'Compliant', nextDue: 'Jun 2025', agency: 'Insurance' },
                        { requirement: 'UCR Registration', status: 'Due Soon', nextDue: 'Feb 2025', agency: 'UCR' },
                        { requirement: 'BOC-3 Process Agent', status: 'Compliant', nextDue: 'Dec 2025', agency: 'FMCSA' }
                    ].map((req, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border ${req.status === 'Compliant' ? 'border-green-200 bg-green-50 dark:bg-green-900/20' :
                            req.status === 'Due Soon' ? 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20' :
                                'border-red-200 bg-red-50 dark:bg-red-900/20'
                            }`}>
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white">{req.requirement}</h4>
                                    <p className="text-sm text-gray-500">Agency: {req.agency}  Due: {req.nextDue}</p>
                                </div>
                                <span className={`px-3 py-1 text-sm rounded-full ${req.status === 'Compliant' ? 'bg-green-100 text-green-800' :
                                    req.status === 'Due Soon' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800'
                                    }`}>
                                    {req.status}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Document Repository */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Legal Document Repository
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                        { name: 'Operating Authority', type: 'PDF', size: '245 KB', updated: '2024-12-15' },
                        { name: 'Insurance Certificate', type: 'PDF', size: '890 KB', updated: '2024-11-01' },
                        { name: 'Broker Bond', type: 'PDF', size: '156 KB', updated: '2024-09-10' },
                        { name: 'Terms of Service', type: 'DOCX', size: '78 KB', updated: '2025-01-01' },
                        { name: 'Privacy Policy', type: 'PDF', size: '124 KB', updated: '2025-01-01' },
                        { name: 'Carrier Agreement Template', type: 'DOCX', size: '92 KB', updated: '2024-10-15' }
                    ].map((doc, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex items-start gap-3">
                                <span className="text-2xl"></span>
                                <div className="flex-1">
                                    <h4 className="font-medium text-gray-900 dark:text-white">{doc.name}</h4>
                                    <p className="text-xs text-gray-500">{doc.type}  {doc.size}</p>
                                    <p className="text-xs text-gray-400">Updated: {doc.updated}</p>
                                </div>
                                <button className="text-blue-600 hover:text-blue-800">
                                    <span></span>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const LegalControlPanel = () => {
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
        { id: 'dashboard', label: 'Legal Dashboard', icon: '', component: LegalDashboardTab },
        { id: 'contracts', label: 'Contract Management', icon: '', component: ContractManagementTab },
        { id: 'disputes', label: 'Dispute Resolution', icon: '', component: DisputeResolutionTab },
        { id: 'compliance', label: 'Compliance', icon: '', component: ComplianceRegulationsTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || LegalDashboardTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Legal Control Panel...</p>
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
                            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Legal Counsel Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Legal & Compliance System
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">{panelData?.stats?.compliance || '98%'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Compliance</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-blue-600">{panelData?.stats?.contracts || 156}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Contracts</p>
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
                                    ? 'border-indigo-600 text-indigo-600 bg-indigo-50 dark:bg-indigo-900/20'
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
                                    onClick={() => handleAction('create_contract', {})}
                                    className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> New Contract
                                </button>
                                <button
                                    onClick={() => handleAction('compliance_check', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Compliance Check
                                </button>
                                <button
                                    onClick={() => handleAction('review_expiring', {})}
                                    className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Review Expiring
                                </button>
                                <button
                                    onClick={() => handleAction('generate_legal_report', {})}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Generate Report
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
                        <span>Legal Counsel Control Panel v2.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LegalControlPanel;
