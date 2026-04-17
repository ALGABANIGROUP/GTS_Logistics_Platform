// frontend/src/components/ConfigurableDashboard.jsx

import React, { useState, useEffect } from 'react';
import { Grid, List, BarChart3, Settings, Plus, X } from 'lucide-react';
import axiosClient from '../api/axiosClient';

const DASHBOARD_WIDGETS = {
    maintenance_health: {
        title: 'System Health',
        component: 'MaintenanceHealthWidget',
        size: 'medium',
        category: 'maintenance'
    },
    maintenance_incidents: {
        title: 'Active Incidents',
        component: 'MaintenanceIncidentsWidget',
        size: 'medium',
        category: 'maintenance'
    },
    shipment_status: {
        title: 'Shipment Status',
        component: 'ShipmentStatusWidget',
        size: 'large',
        category: 'logistics'
    },
    financial_overview: {
        title: 'Financial Overview',
        component: 'FinancialOverviewWidget',
        size: 'medium',
        category: 'finance'
    },
    bot_performance: {
        title: 'Bot Performance',
        component: 'BotPerformanceWidget',
        size: 'large',
        category: 'ai'
    }
};

const LAYOUTS = {
    default: {
        widgets: ['maintenance_health', 'shipment_status', 'financial_overview'],
        grid: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
    },
    compact: {
        widgets: ['maintenance_health', 'maintenance_incidents', 'shipment_status'],
        grid: 'grid-cols-1 md:grid-cols-3'
    },
    detailed: {
        widgets: ['maintenance_health', 'maintenance_incidents', 'shipment_status', 'financial_overview', 'bot_performance'],
        grid: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
    }
};

const ConfigurableDashboard = ({ layout = 'default' }) => {
    const [widgets, setWidgets] = useState([]);
    const [availableWidgets, setAvailableWidgets] = useState([]);
    const [isCustomizing, setIsCustomizing] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardConfig();
    }, [layout]);

    const loadDashboardConfig = async () => {
        try {
            setLoading(true);
            // Load user preferences for dashboard
            const response = await axiosClient.get('/api/v1/users/me/preferences');
            const userLayout = response.data?.preferences?.dashboard_layout || layout;
            const layoutConfig = LAYOUTS[userLayout] || LAYOUTS.default;

            setWidgets(layoutConfig.widgets.map(id => DASHBOARD_WIDGETS[id]).filter(Boolean));
            setAvailableWidgets(Object.entries(DASHBOARD_WIDGETS).map(([id, config]) => ({ id, ...config })));
        } catch (error) {
            console.error('Failed to load dashboard config:', error);
            // Fallback to default
            const layoutConfig = LAYOUTS[layout] || LAYOUTS.default;
            setWidgets(layoutConfig.widgets.map(id => DASHBOARD_WIDGETS[id]).filter(Boolean));
            setAvailableWidgets(Object.entries(DASHBOARD_WIDGETS).map(([id, config]) => ({ id, ...config })));
        } finally {
            setLoading(false);
        }
    };

    const addWidget = (widgetId) => {
        const widget = DASHBOARD_WIDGETS[widgetId];
        if (widget && !widgets.find(w => w.title === widget.title)) {
            setWidgets([...widgets, widget]);
        }
    };

    const removeWidget = (widgetTitle) => {
        setWidgets(widgets.filter(w => w.title !== widgetTitle));
    };

    const getSizeClasses = (size) => {
        switch (size) {
            case 'small': return 'col-span-1';
            case 'medium': return 'col-span-1 md:col-span-2 lg:col-span-2';
            case 'large': return 'col-span-1 md:col-span-2 lg:col-span-3';
            default: return 'col-span-1';
        }
    };

    const renderWidget = (widget) => {
        // Simple scaffold rendering - in real implementation, these would be actual components
        return (
            <div className={`glass-card p-4 ${getSizeClasses(widget.size)}`}>
                <h3 className="text-lg font-semibold text-white mb-2">{widget.title}</h3>
                <div className="text-slate-400">
                    {widget.category} widget content would go here
                </div>
                {isCustomizing && (
                    <button
                        onClick={() => removeWidget(widget.title)}
                        className="absolute top-2 right-2 p-1 text-red-400 hover:text-red-300"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
            </div>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2 text-slate-400">Loading dashboard...</span>
            </div>
        );
    }

    const layoutConfig = LAYOUTS[layout] || LAYOUTS.default;

    return (
        <div className="space-y-4">
            {/* Dashboard Controls */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Dashboard</h2>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setIsCustomizing(!isCustomizing)}
                        className="flex items-center gap-2 px-3 py-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg text-white transition-colors"
                    >
                        <Settings className="w-4 h-4" />
                        {isCustomizing ? 'Done' : 'Customize'}
                    </button>
                </div>
            </div>

            {/* Widget Grid */}
            <div className={`grid gap-4 ${layoutConfig.grid}`}>
                {widgets.map((widget, index) => (
                    <div key={index} className="relative">
                        {renderWidget(widget)}
                    </div>
                ))}
            </div>

            {/* Customization Panel */}
            {isCustomizing && (
                <div className="glass-card p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Add Widgets</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {availableWidgets
                            .filter(widget => !widgets.find(w => w.title === widget.title))
                            .map(widget => (
                                <button
                                    key={widget.id}
                                    onClick={() => addWidget(widget.id)}
                                    className="flex items-center gap-3 p-3 bg-slate-700/30 hover:bg-slate-600/30 rounded-lg text-left transition-colors"
                                >
                                    <Plus className="w-5 h-5 text-blue-400" />
                                    <div>
                                        <div className="text-white font-medium">{widget.title}</div>
                                        <div className="text-slate-400 text-sm capitalize">{widget.category}</div>
                                    </div>
                                </button>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ConfigurableDashboard;
