/**
 *  Freight Broker Control Panel
 * Complete logistics dispatch control center for GTS Logistics
 */
import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "freight_broker";

// Tab definitions
const CONTROL_TABS = [
    { id: "dispatch_dashboard", name: "Dispatch Dashboard", icon: "" },
    { id: "rate_management", name: "Rate Intelligence", icon: "" },
    { id: "carrier_network", name: "Carrier Network", icon: "" },
    { id: "automation", name: "Automation Rules", icon: "" },
];

// Quick actions
const QUICK_ACTIONS = [
    { action: "find_loads", label: " Find Loads", shortcut: "F", color: "blue" },
    { action: "match_carrier", label: " Match Carrier", shortcut: "M", color: "green" },
    { action: "book_shipment", label: " Book Now", shortcut: "B", color: "purple" },
    { action: "emergency_dispatch", label: " Emergency", shortcut: "E", color: "red" },
];

// Automation rules
const AUTOMATION_RULES = [
    {
        id: 1,
        name: "Auto-Dispatch Premium Loads",
        condition: "Rate > $5/mile AND Distance > 500mi",
        action: "Assign to premium carriers automatically",
        active: true,
    },
    {
        id: 2,
        name: "Weather Delay Alert",
        condition: "Severe weather on route",
        action: "Notify shipper & adjust ETA",
        active: true,
    },
    {
        id: 3,
        name: "Capacity Optimization",
        condition: "Truck utilization < 70%",
        action: "Suggest consolidation opportunities",
        active: false,
    },
];

// Scheduled tasks
const SCHEDULED_TASKS = [
    { task: "Load Board Refresh", frequency: "Every 15 minutes", next: "14:30", status: "active" },
    { task: "Carrier Status Update", frequency: "Hourly", next: "15:00", status: "active" },
    { task: "Rate Analysis", frequency: "Every 6 hours", next: "18:00", status: "active" },
    { task: "Performance Report", frequency: "Daily", next: "Tomorrow 06:00", status: "active" },
];

export default function FreightBrokerControlPanel({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeTab, setActiveTab] = useState("dispatch_dashboard");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Control panel data state
    const [panelData, setPanelData] = useState({
        // Header quick stats
        quickStats: {
            activeLoads: 0,
            carriersOnline: 0,
            revenueToday: 0,
            onTimeRate: "0%",
        },
        // Load board
        loadBoard: [],
        // Carrier availability
        carrierAvailability: {
            availableNow: 0,
            enRoute: 0,
            onBreak: 0,
        },
        // Smart matching
        smartMatching: {
            status: "Inactive",
            successRate: "0%",
            recentMatches: [],
        },
        // Market rates
        marketRates: {
            "Toronto-Vancouver": { min: "$4.50", avg: "$4.85", max: "$5.20" },
            "Montreal-Calgary": { min: "$3.80", avg: "$4.20", max: "$4.60" },
            "Vancouver-Edmonton": { min: "$3.40", avg: "$3.95", max: "$4.30" },
            "Toronto-Montreal": { min: "$2.40", avg: "$2.80", max: "$3.20" },
        },
        // Carrier network
        carrierNetwork: {
            totalCarriers: 0,
            premiumCarriers: 0,
            newThisMonth: 0,
            topCarriers: [],
        },
        // System controls
        systemControls: {
            apiStatus: "Disconnected",
            autoDispatch: false,
            notifications: true,
        },
    });

    // Load data from API
    const loadPanelData = useCallback(async () => {
        // Always load demo data for testing/development
        const demoData = {
            quickStats: {
                activeLoads: 24,
                carriersOnline: 18,
                revenueToday: 12500,
                onTimeRate: "96%",
            },
            loadBoard: [
                { id: "LD-001", origin: "Toronto", destination: "Vancouver", equipment: "Dry Van", rate: "$4.85/mile", status: "Available" },
                { id: "LD-002", origin: "Montreal", destination: "Calgary", equipment: "Reefer", rate: "$4.20/mile", status: "Available" },
                { id: "LD-003", origin: "Vancouver", destination: "Edmonton", equipment: "Flatbed", rate: "$3.95/mile", status: "Pending" },
                { id: "LD-004", origin: "Toronto", destination: "Montreal", equipment: "Dry Van", rate: "$2.80/mile", status: "Available" },
            ],
            carrierAvailability: {
                availableNow: 45,
                enRoute: 28,
                onBreak: 12,
            },
            carrierNetwork: {
                totalCarriers: 156,
                premiumCarriers: 42,
                newThisMonth: 8,
                topCarriers: [
                    { name: "TransCanada Express", rating: 4.9, loads: 245 },
                    { name: "Maple Logistics", rating: 4.8, loads: 198 },
                    { name: "Northern Freight", rating: 4.7, loads: 167 },
                ],
            },
            smartMatching: {
                status: "Active",
                successRate: "92%",
                recentMatches: [
                    "LD-001 → TransCanada Express (95% confidence)",
                    "LD-002 → Maple Logistics (88% confidence)",
                ],
            },
        };

        // Load demo data directly without API calls
        setConnected(false);
        setPanelData((prev) => ({
            ...prev,
            ...demoData,
            systemControls: {
                ...prev.systemControls,
                apiStatus: "Demo Mode",
            },
        }));
        setLastUpdate(new Date());
    }, []);

    useEffect(() => {
        loadPanelData();
    }, [loadPanelData]);

    // Connect to APIs (live data only)
    const handleConnectAPIs = () => {
        setConnected(true);
        alert('Connecting to APIs... (Demo Mode active until backend is available)');
        loadPanelData();
    };

    // Execute quick action
    const executeAction = async (action) => {
        // Always execute in demo mode without API calls
        alert(`Action "${action}" executed (Demo Mode)`);
    };

    // Toggle automation rule
    const toggleRule = (ruleId) => {
        // In production, this would call API
        console.log("Toggle rule:", ruleId);
    };

    // Toggle system control
    const toggleControl = (control) => {
        setPanelData((prev) => ({
            ...prev,
            systemControls: {
                ...prev.systemControls,
                [control]: !prev.systemControls[control],
            },
        }));
    };

    return (
        <div className="min-h-screen space-y-4 glass-page">
            {/* Control Panel Header */}
            <header className="glass-panel rounded-2xl border border-white/12 p-5 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    {/* Title Section */}
                    <div className="flex items-center gap-4">
                        <div className="flex h-16 w-16 items-center justify-center rounded-xl glass-panel border border-white/15 text-4xl shadow-lg shadow-black/30">

                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">
                                FREIGHT BROKER CONTROL
                            </h1>
                            <p className="text-sm text-slate-400">
                                Logistics Dispatch Control Center
                            </p>
                        </div>
                    </div>

                    {/* Status & Controls */}
                    <div className="flex items-center gap-3">
                        <ConnectionStatus connected={connected} />
                        <button
                            onClick={loadPanelData}
                            disabled={loading}
                            className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:opacity-50"
                        >
                            <span className={loading ? "animate-spin" : ""}>🔄</span> Refresh
                        </button>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <QuickStat
                        icon=""
                        label="Active Loads"
                        value={panelData.quickStats.activeLoads}
                        color="blue"
                    />
                    <QuickStat
                        icon=""
                        label="Carriers Online"
                        value={panelData.quickStats.carriersOnline}
                        color="green"
                    />
                    <QuickStat
                        icon=""
                        label="Revenue Today"
                        value={`$${panelData.quickStats.revenueToday.toLocaleString()}`}
                        color="gold"
                    />
                    <QuickStat
                        icon=""
                        label="On-time Rate"
                        value={panelData.quickStats.onTimeRate}
                        color="purple"
                    />
                </div>

                {/* Quick Actions */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {QUICK_ACTIONS.map((action) => (
                        <QuickActionButton
                            key={action.action}
                            action={action}
                            onClick={() => executeAction(action.action)}
                            disabled={false}
                        />
                    ))}
                </div>
            </header>

            {/* Demo Mode Banner */}
            <div className="rounded-xl border border-blue-400/30 bg-blue-500/10 px-4 py-3">
                <div className="flex items-center gap-2">
                    <span className="text-blue-400">ℹ️</span>
                    <span className="text-sm font-semibold text-blue-100">
                        Demo Mode Active - Showing sample data for testing and development
                    </span>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex gap-4">
                {/* Tab Navigation */}
                <nav className="hidden w-56 flex-shrink-0 space-y-1 lg:block">
                    {CONTROL_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition glass-panel border border-white/10 ${activeTab === tab.id
                                ? "ring-1 ring-blue-400/40 text-white"
                                : "text-slate-300 hover:border-white/20"
                                }`}
                        >
                            <span className="text-lg">{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </nav>

                {/* Mobile Tab Bar */}
                <div className="mb-4 flex gap-2 overflow-x-auto pb-2 lg:hidden">
                    {CONTROL_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition glass-panel border border-white/10 ${activeTab === tab.id
                                ? "ring-1 ring-blue-400/40 text-white"
                                : "text-slate-300"
                                }`}
                        >
                            <span>{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <main className="flex-1 space-y-4">
                    {activeTab === "dispatch_dashboard" && (
                        <DispatchDashboardTab
                            panelData={panelData}
                            onAction={executeAction}
                            disabled={false}
                        />
                    )}
                    {activeTab === "rate_management" && (
                        <RateManagementTab panelData={panelData} />
                    )}
                    {activeTab === "carrier_network" && (
                        <CarrierNetworkTab panelData={panelData} />
                    )}
                    {activeTab === "automation" && (
                        <AutomationTab
                            rules={AUTOMATION_RULES}
                            tasks={SCHEDULED_TASKS}
                            onToggleRule={toggleRule}
                        />
                    )}
                </main>

                {/* Control Sidebar */}
                <aside className="hidden w-64 flex-shrink-0 space-y-4 xl:block">
                    {/* Load Quick Actions */}
                    <SidebarSection title="LOAD ACTIONS">
                        <SidebarButton icon="" label="New Load" onClick={() => alert('New Load feature coming soon!')} />
                        <SidebarButton icon="" label="Import CSV" onClick={() => alert('Import CSV feature coming soon!')} />
                        <SidebarButton icon="" label="Export Data" onClick={() => alert('Export Data feature coming soon!')} />
                    </SidebarSection>

                    {/* Communication Tools */}
                    <SidebarSection title="COMMUNICATION">
                        <SidebarStatus icon="" label="Rate Chat" status="Online" color="green" />
                        <SidebarStatus icon="" label="e-Sign" status="Ready" color="blue" />
                        <SidebarStatus icon="" label="Live Tracking" status="Active" color="green" />
                    </SidebarSection>

                    {/* System Controls */}
                    <SidebarSection title="SYSTEM CONTROLS">
                        <SidebarToggle
                            icon=""
                            label="API Status"
                            value={panelData.systemControls.apiStatus}
                            active={connected}
                        />
                        <SidebarToggle
                            icon=""
                            label="Auto-Dispatch"
                            value={panelData.systemControls.autoDispatch ? "ON" : "OFF"}
                            active={panelData.systemControls.autoDispatch}
                            onClick={() => toggleControl("autoDispatch")}
                        />
                        <SidebarToggle
                            icon=""
                            label="Notifications"
                            value={panelData.systemControls.notifications ? "ON" : "OFF"}
                            active={panelData.systemControls.notifications}
                            onClick={() => toggleControl("notifications")}
                        />
                    </SidebarSection>
                </aside>
            </div>

            {/* Status Bar Footer */}
            <footer className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4 text-xs">
                    <div className="flex flex-wrap gap-6">
                        <FooterStat label="Last Update" value={lastUpdate?.toLocaleTimeString() || "Never"} />
                        <FooterStat label="API" value={connected ? " Connected" : " Disconnected"} />
                        <FooterStat label="Auto-Dispatch" value={panelData.systemControls.autoDispatch ? " ON" : " OFF"} />
                        <FooterStat label="Match Engine" value={panelData.smartMatching.status} />
                    </div>
                    <Link
                        to="/ai-bots/control?bot=freight_broker&mode=advanced"
                        className="text-blue-400 hover:text-blue-300"
                    >
                        Advanced Settings
                    </Link>
                </div>
            </footer>
        </div>
    );
}

// 
// SUB-COMPONENTS
// 

function ConnectionStatus({ connected }) {
    return (
        <div className="glass-status-badge text-xs font-semibold">
            {connected ? " LIVE" : " OFFLINE"}
        </div>
    );
}

function QuickStat({ icon, label, value, color }) {
    const accentText = {
        blue: "text-blue-200",
        green: "text-emerald-200",
        gold: "text-amber-200",
        purple: "text-purple-200",
    };

    return (
        <div className="glass-panel rounded-lg border border-white/10 p-3 shadow-md">
            <div className="flex items-center gap-2">
                <span className="text-xl">{icon}</span>
                <span className="text-xs font-medium text-slate-400">{label}</span>
            </div>
            <div className={`mt-1 text-xl font-bold text-white ${accentText[color]}`}>{value}</div>
        </div>
    );
}

function QuickActionButton({ action, onClick, disabled }) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className="flex items-center gap-1 rounded-lg glass-btn-secondary glass-btn-sm text-white shadow-lg transition disabled:opacity-50"
        >
            {action.label}
            <kbd className="ml-1 rounded bg-black/30 px-1.5 py-0.5 text-xs font-mono">
                {action.shortcut}
            </kbd>
        </button>
    );
}

function SidebarSection({ title, children }) {
    return (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                {title}
            </h4>
            <div className="space-y-2">{children}</div>
        </div>
    );
}

function SidebarButton({ icon, label, onClick }) {
    return (
        <button 
            onClick={onClick}
            className="flex w-full items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-sm text-slate-300 transition hover:bg-white/10"
        >
            <span>{icon}</span>
            {label}
        </button>
    );
}

function SidebarStatus({ icon, label, status, color }) {
    const dotColors = { green: "bg-emerald-500", blue: "bg-blue-500", red: "bg-rose-500" };
    return (
        <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
            <div className="flex items-center gap-2 text-sm text-slate-300">
                <span>{icon}</span>
                {label}
            </div>
            <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${dotColors[color]}`} />
                <span className="text-xs text-slate-400">{status}</span>
            </div>
        </div>
    );
}

function SidebarToggle({ icon, label, value, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className="flex w-full items-center justify-between rounded-lg bg-white/5 px-3 py-2 transition hover:bg-white/10"
        >
            <div className="flex items-center gap-2 text-sm text-slate-300">
                <span>{icon}</span>
                {label}
            </div>
            <span className={`text-xs font-semibold ${active ? "text-emerald-400" : "text-slate-500"}`}>
                {value}
            </span>
        </button>
    );
}

function FooterStat({ label, value }) {
    return (
        <div>
            <span className="text-slate-500">{label}: </span>
            <span className="font-medium text-slate-300">{value}</span>
        </div>
    );
}

// 
// TAB CONTENT COMPONENTS
// 

function DispatchDashboardTab({ panelData, onAction, disabled }) {
    return (
        <div className="space-y-4">
            {/* Live Dispatch Section */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
                        <span></span> Live Load Board
                    </h3>
                    <Link
                        to="/ai-bots/freight_broker/map"
                        className="text-sm text-blue-400 hover:text-blue-300"
                    >
                        View Map
                    </Link>
                </div>

                {/* Load Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Load ID</th>
                                <th className="pb-3 pr-4">Origin</th>
                                <th className="pb-3 pr-4">Destination</th>
                                <th className="pb-3 pr-4">Equipment</th>
                                <th className="pb-3 pr-4">Rate</th>
                                <th className="pb-3 pr-4">Status</th>
                                <th className="pb-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {panelData.loadBoard.length > 0 ? (
                                panelData.loadBoard.map((load) => (
                                    <tr key={load.id} className="text-slate-300">
                                        <td className="py-3 pr-4 font-mono text-blue-400">{load.id}</td>
                                        <td className="py-3 pr-4">{load.origin}</td>
                                        <td className="py-3 pr-4">{load.destination}</td>
                                        <td className="py-3 pr-4">{load.equipment}</td>
                                        <td className="py-3 pr-4 font-semibold text-emerald-400">{load.rate}</td>
                                        <td className="py-3 pr-4">
                                            <span className={`rounded-full px-2 py-1 text-xs ${load.status === "Available"
                                                ? "bg-emerald-500/20 text-emerald-300"
                                                : "bg-amber-500/20 text-amber-300"
                                                }`}>
                                                {load.status}
                                            </span>
                                        </td>
                                        <td className="py-3">
                                            <div className="flex gap-1">
                                                <button className="rounded bg-white/10 px-2 py-1 text-xs hover:bg-white/20">View</button>
                                                <button className="rounded bg-blue-600/80 px-2 py-1 text-xs hover:bg-blue-500">Assign</button>
                                                <button className="rounded bg-emerald-600/80 px-2 py-1 text-xs hover:bg-emerald-500">Book</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={7} className="py-8 text-center text-slate-500">
                                        Connect APIs to view live load board
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Live Map Preview */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
                        <span></span> Live Freight Map
                    </h3>
                    <div className="flex items-center gap-2">
                        <Link
                            to="/ai-bots/freight_broker/map"
                            className="text-sm text-blue-400 hover:text-blue-300"
                        >
                            Open Full Map
                        </Link>
                        <Link
                            to="/admin/settings?tab=integrations&section=maps"
                            className="text-sm text-slate-300 hover:text-white"
                        >
                            Configure Map
                        </Link>
                    </div>
                </div>
                <div className="flex min-h-[220px] items-center justify-center rounded-lg border border-white/10 bg-slate-950/40 p-6 text-center">
                    <div className="space-y-2">
                        <div className="text-base font-semibold text-white">Map provider not configured</div>
                        <div className="text-sm text-slate-400">
                            Set your map integration to enable live tracking inside the control center.
                        </div>
                    </div>
                </div>
            </div>

            {/* Carrier Availability + Smart Matching Row */}
            <div className="grid gap-4 lg:grid-cols-2">
                {/* Carrier Availability */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> Carrier Availability
                    </h3>
                    <div className="grid grid-cols-3 gap-3">
                        <div className="rounded-lg bg-emerald-500/10 p-3 text-center">
                            <div className="text-2xl font-bold text-emerald-400">
                                {panelData.carrierAvailability.availableNow}
                            </div>
                            <div className="text-xs text-slate-400">Available Now</div>
                        </div>
                        <div className="rounded-lg bg-blue-500/10 p-3 text-center">
                            <div className="text-2xl font-bold text-blue-400">
                                {panelData.carrierAvailability.enRoute}
                            </div>
                            <div className="text-xs text-slate-400">En Route</div>
                        </div>
                        <div className="rounded-lg bg-amber-500/10 p-3 text-center">
                            <div className="text-2xl font-bold text-amber-400">
                                {panelData.carrierAvailability.onBreak}
                            </div>
                            <div className="text-xs text-slate-400">On Break</div>
                        </div>
                    </div>
                </div>

                {/* Smart Matching */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <div className="mb-4 flex items-center justify-between">
                        <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
                            <span></span> Smart Matching Engine
                        </h3>
                        <span className={`rounded-full px-2 py-1 text-xs ${panelData.smartMatching.status === "Active"
                            ? "bg-emerald-500/20 text-emerald-300"
                            : "bg-slate-500/20 text-slate-400"
                            }`}>
                            {panelData.smartMatching.status}
                        </span>
                    </div>
                    <div className="mb-3 text-sm text-slate-400">
                        Success Rate: <span className="font-semibold text-white">{panelData.smartMatching.successRate}</span>
                    </div>
                    <div className="space-y-2">
                        <div className="text-xs text-slate-500">Recent Matches:</div>
                        {panelData.smartMatching.recentMatches.length > 0 ? (
                            panelData.smartMatching.recentMatches.map((match, i) => (
                                <div key={i} className="rounded bg-white/5 px-3 py-2 text-xs text-slate-300">
                                    {match}
                                </div>
                            ))
                        ) : (
                            <div className="text-xs text-slate-500 italic">No recent matches</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function RateManagementTab({ panelData }) {
    const [inputRate, setInputRate] = useState("4.85");
    const estimatedCost = 3.20;
    const profitMargin = ((parseFloat(inputRate) - estimatedCost) / parseFloat(inputRate) * 100).toFixed(1);

    return (
        <div className="space-y-4">
            {/* Market Rates */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Current Market Rates
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Route</th>
                                <th className="pb-3 pr-4 text-center">Min</th>
                                <th className="pb-3 pr-4 text-center">Average</th>
                                <th className="pb-3 text-center">Max</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {Object.entries(panelData.marketRates).map(([route, rates]) => (
                                <tr key={route} className="text-slate-300">
                                    <td className="py-3 pr-4 font-medium">{route}</td>
                                    <td className="py-3 pr-4 text-center text-slate-400">{rates.min}/mi</td>
                                    <td className="py-3 pr-4 text-center font-semibold text-emerald-400">{rates.avg}/mi</td>
                                    <td className="py-3 text-center text-slate-400">{rates.max}/mi</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Profit Calculator */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                    <span></span> Profit Margin Calculator
                </h3>
                <div className="grid gap-4 md:grid-cols-4">
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Input Rate ($/mile)</label>
                        <input
                            type="number"
                            value={inputRate}
                            onChange={(e) => setInputRate(e.target.value)}
                            step="0.01"
                            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Estimated Cost</label>
                        <div className="rounded-lg bg-white/5 px-3 py-2 text-slate-300">
                            ${estimatedCost.toFixed(2)}/mile
                        </div>
                    </div>
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Profit Margin</label>
                        <div className={`rounded-lg px-3 py-2 font-bold ${parseFloat(profitMargin) > 25
                            ? "bg-emerald-500/20 text-emerald-400"
                            : parseFloat(profitMargin) > 10
                                ? "bg-amber-500/20 text-amber-400"
                                : "bg-rose-500/20 text-rose-400"
                            }`}>
                            {profitMargin}%
                        </div>
                    </div>
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Recommendation</label>
                        <div className={`rounded-lg px-3 py-2 text-sm font-semibold ${parseFloat(profitMargin) > 25
                            ? "bg-emerald-500/20 text-emerald-400"
                            : parseFloat(profitMargin) > 10
                                ? "bg-amber-500/20 text-amber-400"
                                : "bg-rose-500/20 text-rose-400"
                            }`}>
                            {parseFloat(profitMargin) > 25
                                ? " Accept - High Margin"
                                : parseFloat(profitMargin) > 10
                                    ? " Review - Medium"
                                    : " Reject - Low Margin"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function CarrierNetworkTab({ panelData }) {
    return (
        <div className="space-y-4">
            {/* Network Stats */}
            <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 text-center backdrop-blur">
                    <div className="text-3xl font-bold text-white">
                        {panelData.carrierNetwork.totalCarriers.toLocaleString()}
                    </div>
                    <div className="text-sm text-slate-400">Total Carriers</div>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 text-center backdrop-blur">
                    <div className="text-3xl font-bold text-amber-400">
                        {panelData.carrierNetwork.premiumCarriers}
                    </div>
                    <div className="text-sm text-slate-400">Premium Carriers</div>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 text-center backdrop-blur">
                    <div className="text-3xl font-bold text-emerald-400">
                        +{panelData.carrierNetwork.newThisMonth}
                    </div>
                    <div className="text-sm text-slate-400">New This Month</div>
                </div>
            </div>

            {/* Top Carriers */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Top Performing Carriers
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Carrier</th>
                                <th className="pb-3 pr-4 text-center">Rating</th>
                                <th className="pb-3 pr-4 text-center">On-Time %</th>
                                <th className="pb-3 pr-4 text-center">Total Loads</th>
                                <th className="pb-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {panelData.carrierNetwork.topCarriers.length > 0 ? (
                                panelData.carrierNetwork.topCarriers.map((carrier, i) => (
                                    <tr key={carrier.name} className="text-slate-300">
                                        <td className="py-3 pr-4">
                                            <div className="flex items-center gap-2">
                                                <span className="text-lg">{i === 0 ? "" : i === 1 ? "" : ""}</span>
                                                <span className="font-mono text-blue-400">{carrier.name}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 pr-4 text-center">
                                            <span className="text-amber-400"></span> {carrier.rating}
                                        </td>
                                        <td className="py-3 pr-4 text-center text-emerald-400">{carrier.onTime}</td>
                                        <td className="py-3 pr-4 text-center">{carrier.loads}</td>
                                        <td className="py-3">
                                            <div className="flex gap-1">
                                                <button className="rounded bg-white/10 px-2 py-1 text-xs hover:bg-white/20">Profile</button>
                                                <button className="rounded bg-blue-600/80 px-2 py-1 text-xs hover:bg-blue-500">Assign Load</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-slate-500">
                                        Connect APIs to view carrier data
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function AutomationTab({ rules, tasks, onToggleRule }) {
    return (
        <div className="space-y-4">
            {/* Automation Rules */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Automation Rules
                </h3>
                <div className="space-y-3">
                    {rules.map((rule) => (
                        <div
                            key={rule.id}
                            className={`rounded-lg border p-4 ${rule.active
                                ? "border-emerald-500/30 bg-emerald-500/10"
                                : "border-white/10 bg-white/5"
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className={`h-2 w-2 rounded-full ${rule.active ? "bg-emerald-500" : "bg-slate-500"}`} />
                                        <span className="font-semibold text-white">{rule.name}</span>
                                    </div>
                                    <div className="mt-2 text-sm text-slate-400">
                                        <span className="text-slate-500">IF:</span> {rule.condition}
                                    </div>
                                    <div className="text-sm text-slate-400">
                                        <span className="text-slate-500">THEN:</span> {rule.action}
                                    </div>
                                </div>
                                <button
                                    onClick={() => onToggleRule(rule.id)}
                                    className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${rule.active
                                        ? "bg-emerald-600 text-white hover:bg-emerald-500"
                                        : "bg-white/10 text-slate-400 hover:bg-white/20"
                                        }`}
                                >
                                    {rule.active ? "Active" : "Inactive"}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Scheduled Tasks */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Scheduled Tasks
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Task</th>
                                <th className="pb-3 pr-4">Frequency</th>
                                <th className="pb-3 pr-4">Next Run</th>
                                <th className="pb-3">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {tasks.map((task, i) => (
                                <tr key={i} className="text-slate-300">
                                    <td className="py-3 pr-4 font-medium">{task.task}</td>
                                    <td className="py-3 pr-4 text-slate-400">{task.frequency}</td>
                                    <td className="py-3 pr-4 text-blue-400">{task.next}</td>
                                    <td className="py-3">
                                        <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300">
                                            {task.status}
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
}
