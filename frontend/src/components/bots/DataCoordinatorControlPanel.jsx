/**
 * DataCoordinatorControlPanel.jsx
 * Data coordinator and analytics control panel
 * Comprehensive Data Coordinator Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'data_coordinator';

// ==================== TAB COMPONENTS ====================

// Tab 1: Data Pipeline
const DataPipelineTab = ({ panelData, onAction }) => {
    const pipelines = panelData?.pipelines || [];
    const activePipelines = pipelines.filter(p => p.status === 'active');

    return (
        <div className="space-y-6">
            {/* Pipeline Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-blue-600">{panelData?.pipelineStats?.total || 12}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Pipelines</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-green-600">{panelData?.pipelineStats?.active || 8}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{panelData?.pipelineStats?.processing || 3}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Processing</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 text-center">
                    <p className="text-3xl font-bold text-red-600">{panelData?.pipelineStats?.failed || 1}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
                </div>
            </div>

            {/* Active Pipelines */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Active Data Pipelines
                    </h3>
                    <button
                        onClick={() => onAction('create_pipeline', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                    >
                        <span></span> New Pipeline
                    </button>
                </div>

                <div className="space-y-4">
                    {(activePipelines.length > 0 ? activePipelines : [
                        { id: 'PL-001', name: 'Load Data Sync', source: 'Load Boards', destination: 'Database', status: 'active', lastRun: '2 min ago', records: 15420 },
                        { id: 'PL-002', name: 'Carrier Updates', source: 'FMCSA API', destination: 'Carrier DB', status: 'active', lastRun: '5 min ago', records: 3250 },
                        { id: 'PL-003', name: 'Rate Intelligence', source: 'DAT/Trucking', destination: 'Analytics', status: 'processing', lastRun: '10 min ago', records: 8900 },
                        { id: 'PL-004', name: 'Financial Data', source: 'Accounting', destination: 'Reports', status: 'active', lastRun: '15 min ago', records: 2100 }
                    ]).map((pipeline, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div className="flex items-center gap-4">
                                    <div className={`p-2 rounded-lg ${pipeline.status === 'active' ? 'bg-green-100 dark:bg-green-900/30' :
                                        pipeline.status === 'processing' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                                            'bg-red-100 dark:bg-red-900/30'
                                        }`}>
                                        <span className="text-2xl">
                                            {pipeline.status === 'active' ? '' : pipeline.status === 'processing' ? '' : ''}
                                        </span>
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-gray-900 dark:text-white">{pipeline.name}</h4>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            {pipeline.source}  {pipeline.destination}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6">
                                    <div className="text-center">
                                        <p className="text-lg font-bold text-blue-600">{pipeline.records?.toLocaleString()}</p>
                                        <p className="text-xs text-gray-500">Records</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-600 dark:text-gray-400">{pipeline.lastRun}</p>
                                        <p className="text-xs text-gray-500">Last Run</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onAction('run_pipeline', { pipelineId: pipeline.id })}
                                            className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
                                        >
                                            Run
                                        </button>
                                        <button
                                            onClick={() => onAction('pause_pipeline', { pipelineId: pipeline.id })}
                                            className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded"
                                        >
                                            Pause
                                        </button>
                                        <button
                                            onClick={() => onAction('configure_pipeline', { pipelineId: pipeline.id })}
                                            className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                        >
                                            Config
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Progress Bar */}
                            {pipeline.status === 'processing' && (
                                <div className="mt-3">
                                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                                        <span>Processing...</span>
                                        <span>67%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '67%' }}></div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Data Flow Diagram */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Data Flow Overview
                </h3>

                <div className="flex flex-wrap items-center justify-center gap-4 p-4">
                    {[
                        { icon: '', label: 'Sources', count: panelData?.sources || 8 },
                        { icon: '', label: '', count: null },
                        { icon: '', label: 'ETL', count: panelData?.transforms || 15 },
                        { icon: '', label: '', count: null },
                        { icon: '', label: 'Storage', count: panelData?.storage || '2.4 TB' },
                        { icon: '', label: '', count: null },
                        { icon: '', label: 'Analytics', count: panelData?.reports || 24 }
                    ].map((step, idx) => (
                        step.label ? (
                            <div key={idx} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg min-w-[100px]">
                                <span className="text-3xl block mb-2">{step.icon}</span>
                                <p className="font-medium text-gray-900 dark:text-white">{step.label}</p>
                                <p className="text-sm text-blue-600 font-bold">{step.count}</p>
                            </div>
                        ) : (
                            <span key={idx} className="text-2xl text-gray-400">{step.icon}</span>
                        )
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 2: Analytics Engine
const AnalyticsEngineTab = ({ panelData, onAction }) => {
    const [selectedMetric, setSelectedMetric] = useState('revenue');

    const metrics = {
        revenue: { label: 'Revenue Analytics', data: panelData?.analytics?.revenue || [] },
        operations: { label: 'Operations Metrics', data: panelData?.analytics?.operations || [] },
        performance: { label: 'Performance KPIs', data: panelData?.analytics?.performance || [] }
    };

    return (
        <div className="space-y-6">
            {/* Analytics Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.analyticsStats?.queries || '24.5K'}</p>
                    <p className="text-sm text-blue-100">Queries Today</p>
                </div>
                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.analyticsStats?.insights || 156}</p>
                    <p className="text-sm text-green-100">AI Insights</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.analyticsStats?.reports || 42}</p>
                    <p className="text-sm text-purple-100">Reports Generated</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-4 shadow-lg text-white">
                    <p className="text-3xl font-bold">{panelData?.analyticsStats?.accuracy || '98.5%'}</p>
                    <p className="text-sm text-orange-100">Prediction Accuracy</p>
                </div>
            </div>

            {/* Metric Selector */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Analytics Dashboard
                    </h3>

                    <div className="flex gap-2">
                        {Object.entries(metrics).map(([key, value]) => (
                            <button
                                key={key}
                                onClick={() => setSelectedMetric(key)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedMetric === key
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {value.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Analytics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { title: 'Total Revenue', value: '$1.2M', change: '+12%', trend: 'up' },
                        { title: 'Active Loads', value: '847', change: '+5%', trend: 'up' },
                        { title: 'Avg Rate/Mile', value: '$2.45', change: '-2%', trend: 'down' },
                        { title: 'On-Time Delivery', value: '94.5%', change: '+1.2%', trend: 'up' },
                        { title: 'Carrier Utilization', value: '78%', change: '+8%', trend: 'up' },
                        { title: 'Customer Satisfaction', value: '4.7/5', change: '+0.2', trend: 'up' }
                    ].map((card, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{card.title}</p>
                            <div className="flex items-end justify-between">
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{card.value}</p>
                                <span className={`flex items-center text-sm font-medium ${card.trend === 'up' ? 'text-green-600' : 'text-red-600'
                                    }`}>
                                    {card.trend === 'up' ? '' : ''} {card.change}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* AI Insights */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    AI-Generated Insights
                </h3>

                <div className="space-y-3">
                    {(panelData?.insights || [
                        { type: 'opportunity', message: 'Chicago-Dallas lane showing 15% rate increase opportunity', priority: 'high' },
                        { type: 'warning', message: 'Carrier capacity expected to decrease 8% next week', priority: 'medium' },
                        { type: 'info', message: 'Customer ABC Corp volume up 25% - consider dedicated capacity', priority: 'low' },
                        { type: 'success', message: 'Fleet utilization improved 12% after route optimization', priority: 'info' }
                    ]).map((insight, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border-l-4 ${insight.type === 'opportunity' ? 'bg-green-50 dark:bg-green-900/20 border-green-500' :
                            insight.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                                insight.type === 'success' ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500' :
                                    'bg-gray-50 dark:bg-gray-700 border-gray-400'
                            }`}>
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                    <span className="text-xl">
                                        {insight.type === 'opportunity' ? '' :
                                            insight.type === 'warning' ? '' :
                                                insight.type === 'success' ? '' : ''}
                                    </span>
                                    <p className="text-gray-900 dark:text-white">{insight.message}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs rounded ${insight.priority === 'high' ? 'bg-red-100 text-red-800' :
                                    insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-gray-100 text-gray-800'
                                    }`}>
                                    {insight.priority}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                <button
                    onClick={() => onAction('generate_insights', {})}
                    className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium"
                >
                    Generate New Insights
                </button>
            </div>
        </div>
    );
};

// Tab 3: Dashboard Manager
const DashboardManagerTab = ({ panelData, onAction }) => {
    const dashboards = panelData?.dashboards || [];

    return (
        <div className="space-y-6">
            {/* Dashboard Gallery */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Dashboard Gallery
                    </h3>
                    <button
                        onClick={() => onAction('create_dashboard', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                    >
                        <span></span> Create Dashboard
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {(dashboards.length > 0 ? dashboards : [
                        { id: 'DB-001', name: 'Executive Summary', type: 'executive', widgets: 8, views: 1250, lastModified: '2 hours ago' },
                        { id: 'DB-002', name: 'Operations Dashboard', type: 'operations', widgets: 12, views: 890, lastModified: '1 day ago' },
                        { id: 'DB-003', name: 'Financial Overview', type: 'finance', widgets: 6, views: 650, lastModified: '3 hours ago' },
                        { id: 'DB-004', name: 'Carrier Performance', type: 'carriers', widgets: 10, views: 420, lastModified: '5 hours ago' },
                        { id: 'DB-005', name: 'Customer Analytics', type: 'customers', widgets: 7, views: 380, lastModified: '1 hour ago' },
                        { id: 'DB-006', name: 'Real-Time Tracking', type: 'tracking', widgets: 5, views: 2100, lastModified: '30 min ago' }
                    ]).map((dashboard, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-lg transition-shadow">
                            <div className="flex items-start justify-between mb-3">
                                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                                    <span className="text-2xl">
                                        {dashboard.type === 'executive' ? '' :
                                            dashboard.type === 'operations' ? '' :
                                                dashboard.type === 'finance' ? '' :
                                                    dashboard.type === 'carriers' ? '' :
                                                        dashboard.type === 'customers' ? '' : ''}
                                    </span>
                                </div>
                                <button className="text-gray-400 hover:text-gray-600">
                                    <span></span>
                                </button>
                            </div>

                            <h4 className="font-bold text-gray-900 dark:text-white mb-2">{dashboard.name}</h4>

                            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                                <span>{dashboard.widgets} widgets</span>
                                <span></span>
                                <span>{dashboard.views} views</span>
                            </div>

                            <p className="text-xs text-gray-500 mb-3">Modified {dashboard.lastModified}</p>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => onAction('open_dashboard', { dashboardId: dashboard.id })}
                                    className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                                >
                                    Open
                                </button>
                                <button
                                    onClick={() => onAction('edit_dashboard', { dashboardId: dashboard.id })}
                                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                >
                                    Edit
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Widget Library */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Widget Library
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                    {[
                        { icon: '', name: 'Bar Chart' },
                        { icon: '', name: 'Line Chart' },
                        { icon: '', name: 'Pie Chart' },
                        { icon: '', name: 'Map View' },
                        { icon: '', name: 'Data Table' },
                        { icon: '', name: 'KPI Card' },
                        { icon: '', name: 'Trend Line' },
                        { icon: '', name: 'Gauge' },
                        { icon: '', name: 'Calendar' },
                        { icon: '', name: 'Timer' },
                        { icon: '', name: 'Alerts' },
                        { icon: '', name: 'Feed' }
                    ].map((widget, idx) => (
                        <button
                            key={idx}
                            onClick={() => onAction('add_widget', { widgetType: widget.name })}
                            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-center"
                        >
                            <span className="text-2xl block mb-1">{widget.icon}</span>
                            <span className="text-xs text-gray-600 dark:text-gray-400">{widget.name}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 4: Data Quality
const DataQualityTab = ({ panelData, onAction }) => {
    const qualityMetrics = panelData?.quality || {};

    return (
        <div className="space-y-6">
            {/* Quality Score */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Data Quality Score
                </h3>

                <div className="flex flex-wrap items-center gap-8">
                    <div className="text-center">
                        <div className="relative inline-flex items-center justify-center w-32 h-32">
                            <svg className="w-32 h-32 transform -rotate-90">
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none" className="text-gray-200 dark:text-gray-700" />
                                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="none"
                                    className="text-green-500"
                                    strokeDasharray={`${(qualityMetrics.overall || 94) * 3.52} 352`} />
                            </svg>
                            <span className="absolute text-3xl font-bold text-gray-900 dark:text-white">
                                {qualityMetrics.overall || 94}%
                            </span>
                        </div>
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Overall Score</p>
                    </div>

                    <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { label: 'Completeness', value: qualityMetrics.completeness || 96, color: 'green' },
                            { label: 'Accuracy', value: qualityMetrics.accuracy || 98, color: 'blue' },
                            { label: 'Consistency', value: qualityMetrics.consistency || 92, color: 'purple' },
                            { label: 'Timeliness', value: qualityMetrics.timeliness || 89, color: 'orange' }
                        ].map((metric, idx) => (
                            <div key={idx} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                <p className={`text-2xl font-bold text-${metric.color}-600`}>{metric.value}%</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{metric.label}</p>
                                <div className="mt-2 w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                    <div className={`bg-${metric.color}-500 h-2 rounded-full`} style={{ width: `${metric.value}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Data Issues */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Data Issues ({panelData?.issues?.length || 5})
                    </h3>
                    <button
                        onClick={() => onAction('run_quality_check', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                    >
                        Run Quality Check
                    </button>
                </div>

                <div className="space-y-3">
                    {(panelData?.issues || [
                        { id: 'ISS-001', type: 'Missing Data', table: 'loads', field: 'delivery_date', count: 23, severity: 'high' },
                        { id: 'ISS-002', type: 'Duplicate Records', table: 'carriers', field: 'mc_number', count: 8, severity: 'medium' },
                        { id: 'ISS-003', type: 'Invalid Format', table: 'customers', field: 'phone', count: 15, severity: 'low' },
                        { id: 'ISS-004', type: 'Outdated Data', table: 'rates', field: 'rate_date', count: 42, severity: 'medium' },
                        { id: 'ISS-005', type: 'Orphan Records', table: 'invoices', field: 'load_id', count: 5, severity: 'high' }
                    ]).map((issue, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border-l-4 ${issue.severity === 'high' ? 'bg-red-50 dark:bg-red-900/20 border-red-500' :
                            issue.severity === 'medium' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                                'bg-gray-50 dark:bg-gray-700 border-gray-400'
                            }`}>
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white">{issue.type}</h4>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        Table: {issue.table}  Field: {issue.field}  {issue.count} records
                                    </p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className={`px-2 py-1 text-xs rounded ${issue.severity === 'high' ? 'bg-red-100 text-red-800' :
                                        issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                        {issue.severity}
                                    </span>
                                    <button
                                        onClick={() => onAction('fix_issue', { issueId: issue.id })}
                                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                                    >
                                        Auto-Fix
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Data Validation Rules */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Validation Rules
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Table</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Check</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {[
                                { rule: 'Required Fields', table: 'loads', type: 'Completeness', status: 'passing', lastCheck: '5 min ago' },
                                { rule: 'Unique MC Numbers', table: 'carriers', type: 'Uniqueness', status: 'passing', lastCheck: '10 min ago' },
                                { rule: 'Valid Phone Format', table: 'customers', type: 'Format', status: 'warning', lastCheck: '15 min ago' },
                                { rule: 'Rate Range Check', table: 'rates', type: 'Range', status: 'passing', lastCheck: '20 min ago' },
                                { rule: 'Foreign Key Integrity', table: 'all', type: 'Referential', status: 'failing', lastCheck: '25 min ago' }
                            ].map((rule, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{rule.rule}</td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rule.table}</td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rule.type}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded ${rule.status === 'passing' ? 'bg-green-100 text-green-800' :
                                            rule.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {rule.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rule.lastCheck}</td>
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

const DataCoordinatorControlPanel = () => {
    const [activeTab, setActiveTab] = useState('pipeline');
    const [panelData, setPanelData] = useState({});
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [actionLog, setActionLog] = useState([]);

    // Fetch panel data
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

    // Handle actions
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
        { id: 'pipeline', label: 'Data Pipeline', icon: '', component: DataPipelineTab },
        { id: 'analytics', label: 'Analytics Engine', icon: '', component: AnalyticsEngineTab },
        { id: 'dashboards', label: 'Dashboard Manager', icon: '', component: DashboardManagerTab },
        { id: 'quality', label: 'Data Quality', icon: '', component: DataQualityTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || DataPipelineTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Data Coordinator Control Panel...</p>
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
                            <div className="p-3 bg-gradient-to-br from-cyan-500 to-teal-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Data Coordinator Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Data coordinator and analytics system
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Quick Stats */}
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-cyan-50 dark:bg-cyan-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-cyan-600">{panelData?.stats?.pipelines || 12}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Pipelines</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">{panelData?.stats?.records || '2.4M'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Records Today</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-purple-600">{panelData?.stats?.quality || '94%'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Data Quality</p>
                                </div>
                            </div>

                            {/* Connection Status */}
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
                                    ? 'border-cyan-600 text-cyan-600 bg-cyan-50 dark:bg-cyan-900/20'
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
                    {/* Main Panel */}
                    <div className="lg:col-span-3">
                        <ActiveTabComponent panelData={panelData} onAction={handleAction} />
                    </div>

                    {/* Sidebar */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Quick Actions */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Quick Actions
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => handleAction('sync_all_pipelines', {})}
                                    className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Sync All Pipelines
                                </button>
                                <button
                                    onClick={() => handleAction('run_analytics', {})}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Run Analytics
                                </button>
                                <button
                                    onClick={() => handleAction('check_data_quality', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Quality Check
                                </button>
                                <button
                                    onClick={() => handleAction('export_data', {})}
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

                        {/* System Health */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> System Health
                            </h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Database</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Healthy</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">ETL Engine</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Running</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Analytics</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Active</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Storage Used</span>
                                    <span className="text-xs text-gray-500">2.4 TB / 5 TB</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-6">
                <div className="max-w-7xl mx-auto px-4 py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <span>Data Coordinator Control Panel v2.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DataCoordinatorControlPanel;
