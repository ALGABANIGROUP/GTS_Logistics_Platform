/**
 * FinanceControlPanel.jsx
 * Finance intelligence control panel
 * Comprehensive Finance Intelligence Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'finance_bot';

// ==================== TAB COMPONENTS ====================

// Tab 1: Financial Dashboard
const FinancialDashboardTab = ({ panelData, onAction }) => {
    const financials = panelData?.financials || {};

    return (
        <div className="space-y-6">
            {/* Key Financial Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${financials.revenue?.toLocaleString() || '1.2M'}</p>
                    <p className="text-sm text-green-100">Total Revenue</p>
                    <p className="text-xs text-green-200 mt-1"> 12% vs last month</p>
                </div>
                <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${financials.profit?.toLocaleString() || '340K'}</p>
                    <p className="text-sm text-blue-100">Net Profit</p>
                    <p className="text-xs text-blue-200 mt-1"> 8% vs last month</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-amber-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${financials.receivables?.toLocaleString() || '285K'}</p>
                    <p className="text-sm text-orange-100">Receivables</p>
                    <p className="text-xs text-orange-200 mt-1">{financials.overdueCount || 12} overdue</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">${financials.payables?.toLocaleString() || '198K'}</p>
                    <p className="text-sm text-purple-100">Payables</p>
                    <p className="text-xs text-purple-200 mt-1">{financials.pendingPayments || 8} pending</p>
                </div>
            </div>

            {/* Cash Flow Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Cash Flow Overview
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-600 dark:text-gray-400">Inflows (This Week)</span>
                            <span className="text-green-600"></span>
                        </div>
                        <p className="text-2xl font-bold text-green-600">${financials.weeklyInflow?.toLocaleString() || '125,400'}</p>
                        <div className="mt-2 text-xs text-gray-500">
                            <span className="text-green-600">+15%</span> vs last week
                        </div>
                    </div>

                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-600 dark:text-gray-400">Outflows (This Week)</span>
                            <span className="text-red-600"></span>
                        </div>
                        <p className="text-2xl font-bold text-red-600">${financials.weeklyOutflow?.toLocaleString() || '89,200'}</p>
                        <div className="mt-2 text-xs text-gray-500">
                            <span className="text-red-600">+8%</span> vs last week
                        </div>
                    </div>

                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-600 dark:text-gray-400">Net Cash Flow</span>
                            <span className="text-blue-600"></span>
                        </div>
                        <p className="text-2xl font-bold text-blue-600">${financials.netCashFlow?.toLocaleString() || '36,200'}</p>
                        <div className="mt-2 text-xs text-gray-500">
                            Operating margin: <span className="text-green-600">28.8%</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Transactions
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(panelData?.transactions || [
                                { date: '2025-01-15', description: 'Load #LD-1234 Payment', type: 'Revenue', amount: 2500, status: 'Completed' },
                                { date: '2025-01-15', description: 'Carrier Payment - Swift', type: 'Expense', amount: -1800, status: 'Pending' },
                                { date: '2025-01-14', description: 'Load #LD-1233 Payment', type: 'Revenue', amount: 3200, status: 'Completed' },
                                { date: '2025-01-14', description: 'Fuel Expense', type: 'Expense', amount: -450, status: 'Completed' },
                                { date: '2025-01-13', description: 'Insurance Premium', type: 'Expense', amount: -1200, status: 'Completed' }
                            ]).map((txn, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{txn.date}</td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{txn.description}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${txn.type === 'Revenue' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {txn.type}
                                        </span>
                                    </td>
                                    <td className={`px-4 py-3 text-sm font-medium ${txn.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {txn.amount > 0 ? '+' : ''}${Math.abs(txn.amount).toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${txn.status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                            }`}>
                                            {txn.status}
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

// Tab 2: Invoicing & Billing
const InvoicingBillingTab = ({ panelData, onAction }) => {
    const [newInvoice, setNewInvoice] = useState({
        customer: '',
        loadId: '',
        amount: '',
        dueDate: ''
    });

    const invoices = panelData?.invoices || [];

    const handleCreateInvoice = () => {
        if (newInvoice.customer && newInvoice.amount) {
            onAction('create_invoice', newInvoice);
            setNewInvoice({ customer: '', loadId: '', amount: '', dueDate: '' });
        }
    };

    return (
        <div className="space-y-6">
            {/* Invoice Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">{panelData?.invoiceStats?.total || 156}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Invoices</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.invoiceStats?.paid || 128}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Paid</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{panelData?.invoiceStats?.pending || 20}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-red-600">{panelData?.invoiceStats?.overdue || 8}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Overdue</p>
                </div>
            </div>

            {/* Create Invoice */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Create New Invoice
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Customer</label>
                        <input
                            type="text"
                            value={newInvoice.customer}
                            onChange={(e) => setNewInvoice({ ...newInvoice, customer: e.target.value })}
                            placeholder="Customer name"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Load ID</label>
                        <input
                            type="text"
                            value={newInvoice.loadId}
                            onChange={(e) => setNewInvoice({ ...newInvoice, loadId: e.target.value })}
                            placeholder="LD-XXXX"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Amount ($)</label>
                        <input
                            type="number"
                            value={newInvoice.amount}
                            onChange={(e) => setNewInvoice({ ...newInvoice, amount: e.target.value })}
                            placeholder="0.00"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Due Date</label>
                        <input
                            type="date"
                            value={newInvoice.dueDate}
                            onChange={(e) => setNewInvoice({ ...newInvoice, dueDate: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                </div>

                <button
                    onClick={handleCreateInvoice}
                    className="mt-4 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                >
                    Create Invoice
                </button>
            </div>

            {/* Invoice List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Invoice List
                    </h3>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onAction('send_reminders', {})}
                            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-medium"
                        >
                            Send Reminders
                        </button>
                        <button
                            onClick={() => onAction('export_invoices', {})}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm font-medium"
                        >
                            Export
                        </button>
                    </div>
                </div>

                <div className="space-y-3">
                    {(invoices.length > 0 ? invoices : [
                        { id: 'INV-001', customer: 'ABC Logistics', loadId: 'LD-1234', amount: 2500, dueDate: '2025-01-20', status: 'Pending', daysOverdue: 0 },
                        { id: 'INV-002', customer: 'XYZ Corp', loadId: 'LD-1235', amount: 3200, dueDate: '2025-01-15', status: 'Overdue', daysOverdue: 3 },
                        { id: 'INV-003', customer: 'Global Trade', loadId: 'LD-1236', amount: 1800, dueDate: '2025-01-25', status: 'Pending', daysOverdue: 0 },
                        { id: 'INV-004', customer: 'FastShip Inc', loadId: 'LD-1237', amount: 4100, dueDate: '2025-01-10', status: 'Paid', daysOverdue: 0 }
                    ]).map((invoice, idx) => (
                        <div key={idx} className={`p-4 border rounded-lg ${invoice.status === 'Overdue' ? 'border-red-300 bg-red-50 dark:bg-red-900/20' :
                            invoice.status === 'Paid' ? 'border-green-300 bg-green-50 dark:bg-green-900/20' :
                                'border-gray-200 dark:border-gray-700'
                            }`}>
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-blue-600">{invoice.id}</span>
                                        <span className={`px-2 py-0.5 text-xs rounded ${invoice.status === 'Paid' ? 'bg-green-100 text-green-800' :
                                            invoice.status === 'Overdue' ? 'bg-red-100 text-red-800' :
                                                'bg-yellow-100 text-yellow-800'
                                            }`}>
                                            {invoice.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        {invoice.customer}  Load: {invoice.loadId}
                                    </p>
                                </div>

                                <div className="flex items-center gap-6">
                                    <div className="text-right">
                                        <p className="text-xl font-bold text-gray-900 dark:text-white">${invoice.amount.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">Due: {invoice.dueDate}</p>
                                    </div>

                                    {invoice.status !== 'Paid' && (
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => onAction('mark_paid', { invoiceId: invoice.id })}
                                                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
                                            >
                                                Mark Paid
                                            </button>
                                            <button
                                                onClick={() => onAction('send_reminder', { invoiceId: invoice.id })}
                                                className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded"
                                            >
                                                Remind
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 3: Expense Management
const ExpenseManagementTab = ({ panelData, onAction }) => {
    const [newExpense, setNewExpense] = useState({
        category: 'Operations',
        description: '',
        amount: '',
        date: ''
    });

    const expenses = panelData?.expenses || [];
    const categories = ['Operations', 'Fuel', 'Maintenance', 'Insurance', 'Payroll', 'Office', 'Marketing', 'Other'];

    return (
        <div className="space-y-6">
            {/* Expense Summary by Category */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Expense Summary by Category
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { category: 'Carrier Payments', amount: 85000, percent: 45, color: 'blue' },
                        { category: 'Fuel', amount: 28000, percent: 15, color: 'yellow' },
                        { category: 'Insurance', amount: 18000, percent: 10, color: 'purple' },
                        { category: 'Operations', amount: 15000, percent: 8, color: 'green' },
                        { category: 'Payroll', amount: 25000, percent: 13, color: 'orange' },
                        { category: 'Maintenance', amount: 8000, percent: 4, color: 'red' },
                        { category: 'Marketing', amount: 5000, percent: 3, color: 'pink' },
                        { category: 'Other', amount: 4000, percent: 2, color: 'gray' }
                    ].map((cat, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{cat.category}</span>
                                <span className="text-xs text-gray-500">{cat.percent}%</span>
                            </div>
                            <p className={`text-xl font-bold text-${cat.color}-600`}>${cat.amount.toLocaleString()}</p>
                            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                <div className={`bg-${cat.color}-500 h-2 rounded-full`} style={{ width: `${cat.percent}%` }}></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Add Expense */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Record New Expense
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                        <select
                            value={newExpense.category}
                            onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                        <input
                            type="text"
                            value={newExpense.description}
                            onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                            placeholder="Expense description"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Amount ($)</label>
                        <input
                            type="number"
                            value={newExpense.amount}
                            onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                            placeholder="0.00"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date</label>
                        <input
                            type="date"
                            value={newExpense.date}
                            onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                </div>

                <button
                    onClick={() => onAction('record_expense', newExpense)}
                    className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
                >
                    Record Expense
                </button>
            </div>

            {/* Recent Expenses */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Expenses
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(expenses.length > 0 ? expenses : [
                                { date: '2025-01-15', category: 'Carrier Payment', description: 'Swift Transport - Load #1234', amount: 1800 },
                                { date: '2025-01-14', category: 'Fuel', description: 'Fleet fuel - Week 2', amount: 3500 },
                                { date: '2025-01-14', category: 'Insurance', description: 'Monthly premium', amount: 1500 },
                                { date: '2025-01-13', category: 'Maintenance', description: 'Truck #T-101 service', amount: 850 }
                            ]).map((expense, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{expense.date}</td>
                                    <td className="px-4 py-3">
                                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">{expense.category}</span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{expense.description}</td>
                                    <td className="px-4 py-3 text-sm font-medium text-red-600">-${expense.amount.toLocaleString()}</td>
                                    <td className="px-4 py-3">
                                        <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
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

// Tab 4: Financial Reports
const FinancialReportsTab = ({ panelData, onAction }) => {
    const [reportType, setReportType] = useState('profit_loss');
    const [dateRange, setDateRange] = useState({ start: '', end: '' });

    return (
        <div className="space-y-6">
            {/* Report Generator */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Generate Financial Report
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Report Type</label>
                        <select
                            value={reportType}
                            onChange={(e) => setReportType(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="profit_loss">Profit & Loss</option>
                            <option value="balance_sheet">Balance Sheet</option>
                            <option value="cash_flow">Cash Flow Statement</option>
                            <option value="accounts_receivable">Accounts Receivable</option>
                            <option value="accounts_payable">Accounts Payable</option>
                            <option value="expense_report">Expense Report</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label>
                        <input
                            type="date"
                            value={dateRange.start}
                            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label>
                        <input
                            type="date"
                            value={dateRange.end}
                            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={() => onAction('generate_report', { type: reportType, ...dateRange })}
                            className="w-full px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                        >
                            Generate Report
                        </button>
                    </div>
                </div>
            </div>

            {/* Quick Reports */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Quick Reports
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { name: 'Daily Summary', icon: '', desc: 'Today\'s financial overview' },
                        { name: 'Weekly P&L', icon: '', desc: 'This week\'s profit & loss' },
                        { name: 'Monthly Statement', icon: '', desc: 'Full monthly financial statement' },
                        { name: 'AR Aging Report', icon: '', desc: 'Accounts receivable aging' },
                        { name: 'AP Summary', icon: '', desc: 'Accounts payable summary' },
                        { name: 'Tax Report', icon: '', desc: 'Tax-ready financial data' }
                    ].map((report, idx) => (
                        <button
                            key={idx}
                            onClick={() => onAction('quick_report', { report: report.name })}
                            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md hover:border-blue-500 transition-all text-left"
                        >
                            <span className="text-2xl block mb-2">{report.icon}</span>
                            <h4 className="font-medium text-gray-900 dark:text-white">{report.name}</h4>
                            <p className="text-sm text-gray-500">{report.desc}</p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Saved Reports */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Saved Reports
                </h3>

                <div className="space-y-3">
                    {[
                        { name: 'Q4 2024 Financial Summary', type: 'Profit & Loss', date: '2025-01-01', size: '2.4 MB' },
                        { name: 'December 2024 P&L', type: 'Profit & Loss', date: '2025-01-02', size: '1.8 MB' },
                        { name: 'Annual Tax Report 2024', type: 'Tax Report', date: '2025-01-10', size: '5.2 MB' },
                        { name: 'January Week 1 Summary', type: 'Weekly Report', date: '2025-01-07', size: '890 KB' }
                    ].map((report, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg flex items-center justify-between hover:shadow-md transition-shadow">
                            <div className="flex items-center gap-4">
                                <span className="text-2xl"></span>
                                <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white">{report.name}</h4>
                                    <p className="text-sm text-gray-500">{report.type}  {report.date}  {report.size}</p>
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded">View</button>
                                <button className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded">Download</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const FinanceControlPanel = () => {
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
        { id: 'dashboard', label: 'Financial Dashboard', icon: '', component: FinancialDashboardTab },
        { id: 'invoicing', label: 'Invoicing & Billing', icon: '', component: InvoicingBillingTab },
        { id: 'expenses', label: 'Expense Management', icon: '', component: ExpenseManagementTab },
        { id: 'reports', label: 'Financial Reports', icon: '', component: FinancialReportsTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || FinancialDashboardTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Finance Control Panel...</p>
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
                            <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Finance Intelligence Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Financial intelligence system
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">${panelData?.stats?.revenue?.toLocaleString() || '1.2M'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Revenue</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-orange-600">${panelData?.stats?.receivables?.toLocaleString() || '285K'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Receivables</p>
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
                                    ? 'border-green-600 text-green-600 bg-green-50 dark:bg-green-900/20'
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
                                    onClick={() => handleAction('process_payments', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Process Payments
                                </button>
                                <button
                                    onClick={() => handleAction('generate_invoices', {})}
                                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Generate Invoices
                                </button>
                                <button
                                    onClick={() => handleAction('reconcile_accounts', {})}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Reconcile Accounts
                                </button>
                                <button
                                    onClick={() => handleAction('export_financial_data', {})}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Export Data
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
                        <span>Finance Intelligence Control Panel v2.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FinanceControlPanel;
