/* eslint-disable react/prop-types */

/**
 *  GTS - General Manager Control Panel
 * General executive management command center for GTS Logistics
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "general_manager";
const USE_MOCK_DATA = true;

// Tab definitions
const CONTROL_TABS = [
    { id: "dashboard", name: "Dashboard", icon: "" },
    { id: "operations", name: "Operations", icon: "" },
    { id: "reports", name: "Reports", icon: "" },
    { id: "team", name: "Team", icon: "" },
];

// Quick actions
const QUICK_ACTIONS = [
    { name: "Daily Briefing", icon: "", action: "daily_briefing" },
    { name: "Team Status", icon: "", action: "bots_status" },
    { name: "Forecast", icon: "", action: "forecast" },
    { name: "Generate Report", icon: "", action: "generate_report" },
];

const DEFAULT_DASHBOARD = {
    unified_kpi: {
        current: 87.5,
        previous: 84.2,
        change: "+3.3",
        target: 90.0,
        status: "improving",
    },
    department_performance: {
        operations: { score: 92.3, change: "+2.1", status: "excellent" },
        finance: { score: 85.7, change: "+1.5", status: "good" },
        customers: { score: 78.4, change: "-0.8", status: "warning" },
        safety: { score: 95.6, change: "+3.2", status: "excellent" },
    },
    critical_alerts: [
        { id: "ALT001", title: "Delayed shipment cluster on Riyadh lanes", severity: "high", source: "dispatcher", action_required: true },
        { id: "ALT002", title: "VIP customer escalation needs immediate callback", severity: "high", source: "customer_service", action_required: true },
    ],
    strategic_recommendations: [
        { id: "REC001", title: "Hire 3 additional Riyadh drivers", priority: "high", impact: "+15% route capacity", owner: "HR / Operations" },
        { id: "REC002", title: "Launch US market expansion pilot", priority: "high", impact: "+25% international revenue opportunity", owner: "Expansion Office" },
        { id: "REC003", title: "Promote 3 high-performing partners", priority: "medium", impact: "+10% partner retention", owner: "Partner Success" },
    ],
    operational_snapshot: {
        total_shipments: 1247,
        on_time_delivery: 94.2,
        delayed_shipments: 75,
        active_drivers: 85,
    },
    team_status: {
        total_bots: 7,
        active_bots: 7,
        inactive_bots: 0,
        details: [
            { bot: "dispatcher", status: "active", reports_today: 41 },
            { bot: "customer_service", status: "active", reports_today: 28 },
            { bot: "sales_bot", status: "active", reports_today: 16 },
            { bot: "safety_bot", status: "active", reports_today: 12 },
        ],
    },
};

const buildPanelData = (statusPayload = {}, dashboardPayload = null) => {
    const safeDashboard =
        dashboardPayload && typeof dashboardPayload === "object"
            ? dashboardPayload
            : DEFAULT_DASHBOARD;
    const teamDetails =
        statusPayload?.teams ||
        safeDashboard?.team_status?.details ||
        DEFAULT_DASHBOARD.team_status.details;

    return {
        metrics: statusPayload?.metrics || {
            activeTeams: { value: safeDashboard?.team_status?.active_bots || 0, target: 15, status: "active" },
            totalEmployees: { value: 187, target: 200, status: "active" },
            operationsStatus: { value: `${safeDashboard?.department_performance?.operations?.score || 0}%`, trend: "positive" },
            responseTime: { value: "0.4h", trend: "neutral" },
        },
        teams: teamDetails,
        pending:
            statusPayload?.pending ||
            safeDashboard?.critical_alerts ||
            DEFAULT_DASHBOARD.critical_alerts,
        activities:
            statusPayload?.activities ||
            safeDashboard?.strategic_recommendations ||
            DEFAULT_DASHBOARD.strategic_recommendations,
        reports: statusPayload?.reports || [],
        dashboard: {
            ...DEFAULT_DASHBOARD,
            ...safeDashboard,
            team_status: {
                ...DEFAULT_DASHBOARD.team_status,
                ...(safeDashboard?.team_status || {}),
                details: teamDetails,
            },
        },
    };
};

export default function GeneralManagerControlPanel({ mode = "active" }) {
    const isPreview = mode === "preview";
    const usingMockData = isPreview || USE_MOCK_DATA;
    const [activeTab, setActiveTab] = useState("dashboard");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [actionLog, setActionLog] = useState([]);

    // Control panel data state
    const [panelData, setPanelData] = useState({
        // Key metrics
        metrics: {
            activeTeams: { value: 0, target: 0, status: "active" },
            totalEmployees: { value: 0, target: 0, status: "active" },
            operationsStatus: { value: "0%", trend: "neutral" },
            responseTime: { value: "0h", trend: "neutral" },
        },
        // Team information
        teams: [],
        // Pending items
        pending: [],
        // Recent activities
        activities: [],
        // Reports available
        reports: [],
    });

    // Load panel data
    const loadPanelData = useCallback(async () => {
        if (usingMockData) {
            setPanelData(buildPanelData());
            setConnected(true);
            setLastUpdate(new Date());
            return;
        }

        setLoading(true);
        try {
            const [statusResponse, dashboardResponse] = await Promise.allSettled([
                axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
                axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
                    message: "load executive dashboard",
                    context: { action: "dashboard" },
                    meta: { source: "general_manager_control_panel" },
                }),
            ]);

            const statusPayload =
                statusResponse.status === "fulfilled"
                    ? statusResponse.value?.data?.status || {}
                    : {};
            const dashboardPayload =
                dashboardResponse.status === "fulfilled"
                    ? dashboardResponse.value?.data?.result || {}
                    : null;

            if (statusResponse.status === "rejected") {
                console.warn("General Manager status load failed:", statusResponse.reason);
            }
            if (dashboardResponse.status === "rejected") {
                console.warn("General Manager dashboard run failed, using fallback dashboard:", dashboardResponse.reason);
            }

            setPanelData(buildPanelData(statusPayload, dashboardPayload));
            setConnected(statusResponse.status === "fulfilled" || dashboardResponse.status === "fulfilled");
            setLastUpdate(new Date());
        } catch (err) {
            console.warn("Panel data load error:", err);
            setPanelData(buildPanelData());
            setConnected(false);
        } finally {
            setLoading(false);
        }
    }, [usingMockData]);

    // Load data on mount
    useEffect(() => {
        loadPanelData();
        const interval = setInterval(loadPanelData, 30000);
        return () => clearInterval(interval);
    }, [loadPanelData]);

    // Handle action execution
    const handleAction = useCallback(async (action, params = {}) => {
        const logEntry = {
            id: Date.now(),
            action,
            params,
            timestamp: new Date().toISOString(),
            status: "pending",
        };

        setActionLog(prev => [logEntry, ...prev.slice(0, 19)]);

        if (usingMockData) {
            const mockResult = {
                ok: true,
                mode: "offline",
                action,
                message: `${action} completed in offline mode`,
                generated_at: new Date().toISOString(),
            };

            setActionLog(prev =>
                prev.map(log =>
                    log.id === logEntry.id
                        ? { ...log, status: "success", result: mockResult }
                        : log
                )
            );

            return mockResult;
        }

        try {
            const response = await axiosClient.post(
                `/api/v1/ai/bots/available/${BOT_KEY}/run`,
                {
                    message: `run ${action}`,
                    context: { action, ...params },
                    meta: { source: "general_manager_control_panel" },
                }
            );

            setActionLog(prev =>
                prev.map(log =>
                    log.id === logEntry.id
                        ? { ...log, status: "success", result: response.data?.result || response.data }
                        : log
                )
            );

            loadPanelData();
            return response.data;
        } catch (error) {
            setActionLog(prev =>
                prev.map(log =>
                    log.id === logEntry.id
                        ? { ...log, status: "error", error: error.message }
                        : log
                )
            );
            throw error;
        }
    }, [loadPanelData, usingMockData]);

    {/* Render loading state */ }
    if (
        loading &&
        !(
            panelData &&
            panelData.metrics &&
            panelData.metrics.activeTeams &&
            typeof panelData.metrics.activeTeams.value !== "undefined" &&
            panelData.metrics.activeTeams.value
        )
    ) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-400">Loading General Manager Dashboard...</p>
                </div>
            </div>
        );
    }

    // Render main panel
    return (
        <div className="min-h-screen bg-gray-900">
            {/* Header */}
            <div className="bg-gray-800 shadow-lg border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <span className="text-4xl"></span>
                            <div>
                                <h1 className="text-3xl font-bold text-white">
                                    General Manager
                                </h1>
                                <p className="text-gray-400 text-sm">
                                    Executive management command center
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span
                                className={`px-3 py-1 rounded-full text-sm font-semibold ${connected
                                    ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                                    : "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200"
                                    }`}
                            >
                                {usingMockData ? " Seed Data" : connected ? " Connected" : " Offline Mode"}
                            </span>
                            {lastUpdate && (
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                    Last sync: {lastUpdate.toLocaleTimeString()}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                        <p className="text-sm text-gray-400 mb-1">Active Teams</p>
                        <p className="text-2xl font-bold text-white">{panelData?.metrics?.activeTeams?.value || 0}</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                        <p className="text-sm text-gray-400 mb-1">Total Employees</p>
                        <p className="text-2xl font-bold text-white">{panelData?.metrics?.totalEmployees?.value || 0}</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                        <p className="text-sm text-gray-400 mb-1">Operations Running</p>
                        <p className="text-2xl font-bold text-white">{panelData?.metrics?.operationsStatus?.value || '0%'}</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                        <p className="text-sm text-gray-400 mb-1">Avg Response Time</p>
                        <p className="text-2xl font-bold text-white">{panelData?.metrics?.responseTime?.value || '0h'}</p>
                    </div>
                </div>
            </div>

            {/* Tabs Navigation */}
            <div className="bg-gray-800 border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex gap-8 overflow-x-auto">
                        {CONTROL_TABS.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-4 py-4 font-semibold text-sm whitespace-nowrap border-b-2 transition-colors ${activeTab === tab.id
                                    ? "border-blue-500 text-blue-400"
                                    : "border-transparent text-gray-400 hover:text-white"
                                    }`}
                            >
                                <span className="mr-2">{tab.icon}</span>
                                {tab.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Main Content Area */}
                    <div className="lg:col-span-3">
                        {/* Dashboard Tab */}
                        {activeTab === "dashboard" && (
                            <div className="space-y-6">
                                <div className="bg-gray-800 rounded-lg p-6 shadow border border-gray-700">
                                    <h2 className="text-xl font-bold text-white mb-4">
                                        Executive Overview
                                    </h2>
                                    <p className="text-gray-400">
                                        Monitor all organizational activities, team performance, and strategic metrics
                                        in real-time.
                                    </p>
                                </div>

                                <div className="bg-gray-800 rounded-lg p-6 shadow border border-gray-700">
                                    <h3 className="text-lg font-semibold text-white mb-4">
                                        Current Status
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="p-3 bg-blue-900/30 rounded border border-blue-800">
                                            <p className="text-sm text-gray-400">Active Departments</p>
                                            <p className="text-2xl font-bold text-blue-400">{panelData?.dashboard?.team_status?.active_bots || 0}</p>
                                        </div>
                                        <div className="p-3 bg-green-900/30 rounded border border-green-800">
                                            <p className="text-sm text-gray-400">Efficiency Rating</p>
                                            <p className="text-2xl font-bold text-green-400">{panelData?.dashboard?.unified_kpi?.current || 0}%</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Operations Tab */}
                        {activeTab === "operations" && (
                            <div className="space-y-6">
                                <div className="bg-gray-800 rounded-lg p-6 shadow border border-gray-700">
                                    <h2 className="text-xl font-bold text-white mb-4">
                                        Operations Management
                                    </h2>
                                    <div className="space-y-3">
                                        <div className="p-3 border border-gray-700 rounded">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="font-semibold text-white">
                                                    Freight Processing
                                                </span>
                                                <span className="text-green-600 dark:text-green-400">{panelData?.dashboard?.department_performance?.operations?.score || 0}%</span>
                                            </div>
                                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded h-2">
                                                <div className="bg-green-600 h-2 rounded" style={{ width: `${panelData?.dashboard?.department_performance?.operations?.score || 0}%` }}></div>
                                            </div>
                                        </div>
                                        <div className="p-3 border border-gray-700 rounded">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="font-semibold text-white">
                                                    Delivery On-Time
                                                </span>
                                                <span className="text-blue-400">{panelData?.dashboard?.operational_snapshot?.on_time_delivery || 0}%</span>
                                            </div>
                                            <div className="w-full bg-gray-700 rounded h-2">
                                                <div className="bg-blue-500 h-2 rounded" style={{ width: `${panelData?.dashboard?.operational_snapshot?.on_time_delivery || 0}%` }}></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Reports Tab */}
                        {activeTab === "reports" && (
                            <div className="space-y-6">
                                <div className="bg-gray-800 rounded-lg p-6 shadow border border-gray-700">
                                    <h2 className="text-xl font-bold text-white mb-4">
                                        Reports
                                    </h2>
                                    <p className="text-gray-400 mb-4">Available reports:</p>
                                    <div className="space-y-2">
                                        {["Daily Summary", "Weekly Review", "Monthly Analysis", "Quarterly Report"].map(
                                            (report, idx) => (
                                                <button
                                                    key={idx}
                                                    className="w-full p-3 text-left bg-gray-700 hover:bg-gray-600 rounded border border-gray-600 text-gray-200 transition-colors"
                                                >
                                                    {report}
                                                </button>
                                            )
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Team Tab */}
                        {activeTab === "team" && (
                            <div className="space-y-6">
                                <div className="bg-gray-800 rounded-lg p-6 shadow border border-gray-700">
                                    <h2 className="text-xl font-bold text-white mb-4">
                                        Team Management
                                    </h2>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {(panelData?.teams?.length ? panelData.teams : [
                                            { bot: "operations", status: "active" },
                                            { bot: "finance", status: "active" },
                                            { bot: "customer_service", status: "active" },
                                            { bot: "intelligence", status: "active" },
                                        ]).map(
                                            (role, idx) => (
                                                <div
                                                    key={idx}
                                                    className="p-4 bg-gray-700 rounded border border-gray-600"
                                                >
                                                    <p className="font-semibold text-white">{role.bot || role.name || "Team"}</p>
                                                    <p className="text-xs text-gray-400 mt-1">
                                                        {(role.status || "active")}  Last sync: now
                                                    </p>
                                                </div>
                                            )
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Quick Actions */}
                        <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                            <h3 className="font-semibold text-white mb-3"> Quick Actions</h3>
                            <div className="space-y-2">
                                {QUICK_ACTIONS.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleAction(action.action)}
                                        className="w-full p-2 text-left text-sm bg-blue-900/30 hover:bg-blue-900/50 text-blue-400 rounded border border-blue-800 transition-colors"
                                    >
                                        <span className="mr-2">{action.icon}</span>
                                        {action.name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="bg-gray-800 rounded-lg p-4 shadow border border-gray-700">
                            <h3 className="font-semibold text-white mb-3"> Activity Log</h3>
                            <div className="space-y-2 max-h-60 overflow-y-auto">
                                {actionLog.length === 0 ? (
                                    <p className="text-xs text-gray-400">No recent activity</p>
                                ) : (
                                    actionLog.map(log => (
                                        <div
                                            key={log.id}
                                            className={`p-2 rounded text-xs ${log.status === "success"
                                                ? "bg-green-900/30 text-green-300 border border-green-800"
                                                : log.status === "error"
                                                    ? "bg-red-900/30 text-red-300 border border-red-800"
                                                    : "bg-gray-700 text-gray-300 border border-gray-600"
                                                }`}
                                        >
                                            <p className="font-semibold">{log.action}</p>
                                            <p className="text-xs opacity-75">
                                                {new Date(log.timestamp).toLocaleTimeString()}
                                            </p>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
