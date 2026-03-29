/**
 * Maintenance Dev Control Panel
 * System maintenance command center
 */
import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";
import { API_BASE_URL } from "../../config/env";

const BOT_KEY = "maintenance_dev";
const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

// Tab definitions
const CONTROL_TABS = [
    { id: "infrastructure", name: "Infrastructure", icon: "" },
    { id: "development", name: "Operations", icon: "" },
    { id: "security", name: "Security", icon: "" },
    { id: "diagnostics", name: "Diagnostics", icon: "" },
];

// Emergency controls
const EMERGENCY_CONTROLS = [
    { control: "system_reboot", label: "Reboot System", requiresAuth: true, color: "amber" },
    { control: "failover", label: "Failover", requiresAuth: true, color: "purple" },
    { control: "backup_restore", label: "Backup Restore", requiresAuth: true, color: "blue" },
    { control: "lockdown", label: "Lockdown", requiresAuth: true, color: "red" },
];

// Automation scripts
const AUTOMATION_SCRIPTS = [
    { script: "cleanup_temp_files", label: "Cleanup Temp Files", frequency: "Daily", lastRun: "2h ago" },
    { script: "database_optimize", label: "Optimize Database", frequency: "Weekly", lastRun: "3d ago" },
    { script: "backup_verification", label: "Verify Backup", frequency: "Daily", lastRun: "6h ago" },
    { script: "security_scan", label: "Security Scan", frequency: "Daily", lastRun: "12h ago" },
];

// Scaling policies
const SCALING_POLICIES = [
    { metric: "CPU > 70%", action: "+2 instances", active: true },
    { metric: "Memory > 80%", action: "+1 instance", active: true },
    { metric: "Queue > 1000", action: "+3 instances", active: true },
    { metric: "Response > 500ms", action: "Alert only", active: false },
];

export default function DevMaintenanceControlPanel({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeTab, setActiveTab] = useState("infrastructure");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [confirmAction, setConfirmAction] = useState(null);

    // Automation scripts and logs state
    const [automationScripts, setAutomationScripts] = useState(AUTOMATION_SCRIPTS);
    const [systemLogs, setSystemLogs] = useState([])

    // Control panel data state
    const [panelData, setPanelData] = useState({
        // System health
        systemHealth: {
            apiGateway: { status: "unknown", latency: "0ms" },
            database: { status: "unknown", usage: "0%" },
            cache: { status: "unknown", hitRate: "0%" },
            messageQueue: { status: "unknown", backlog: "0" },
        },
        // Infrastructure
        infrastructure: {
            servers: [],
            autoScaling: {
                currentInstances: 0,
                maxInstances: 0,
            },
        },
        // System metrics
        systemMetrics: {
            uptime: "0%",
            errorRate: "0%",
            responseTime: "0ms",
            activeConnections: "0",
        },
        // Development pipeline
        pipeline: {
            stages: [],
            upcomingReleases: [],
        },
        // Tech debt
        techDebt: {
            totalPoints: 0,
            criticalItems: [],
            resolutionPlan: "",
        },
        // Security
        security: {
            activeThreats: 0,
            blockedAttacks: 0,
            lastIncident: "N/A",
            compliance: {},
        },
    });

    // Load data from API
    const loadPanelData = useCallback(async () => {
        if (isPreview) return;
        setLoading(true);
        try {
            const [statusRes, healthRes, scriptsRes, logsRes] = await Promise.all([
                axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`).catch(() => null),
                axiosClient.get("/api/v1/system/health").catch(() => null),
                axiosClient.get("/api/v1/system/automation-scripts").catch(() => null),
                axiosClient.get("/api/v1/system/logs?limit=50").catch(() => null),
            ]);

            if (statusRes?.data || healthRes?.data) {
                setConnected(true);
                // Update with real data when available
            }

            // Set automation scripts from API
            if (scriptsRes?.data?.scripts) {
                setAutomationScripts(scriptsRes.data.scripts);
            }

            // Set system logs from API
            if (logsRes?.data?.logs) {
                setSystemLogs(logsRes.data.logs);
            }

            setLastUpdate(new Date());
        } catch (err) {
            console.warn("Panel data load error:", err);
        } finally {
            setLoading(false);
        }
    }, [isPreview]);

    useEffect(() => {
        loadPanelData();
    }, [loadPanelData]);

    // Connect to APIs (simulation)
    const handleConnectAPIs = () => {
        setConnected(true);
        setPanelData({
            systemHealth: {
                apiGateway: { status: "healthy", latency: "45ms" },
                database: { status: "warning", usage: "87%" },
                cache: { status: "healthy", hitRate: "94%" },
                messageQueue: { status: "healthy", backlog: "0" },
            },
            infrastructure: {
                servers: [
                    { name: "API-01", cpu: "42%", memory: "65%", status: "Healthy", region: "us-east-1" },
                    { name: "API-02", cpu: "38%", memory: "58%", status: "Healthy", region: "us-east-1" },
                    { name: "DB-01", cpu: "78%", memory: "89%", status: "Warning", region: "us-east-1" },
                    { name: "DB-02", cpu: "45%", memory: "72%", status: "Healthy", region: "us-west-2" },
                    { name: "CACHE-01", cpu: "22%", memory: "45%", status: "Healthy", region: "us-east-1" },
                ],
                autoScaling: {
                    currentInstances: 8,
                    maxInstances: 12,
                },
            },
            systemMetrics: {
                uptime: "99.97%",
                errorRate: "0.03%",
                responseTime: "142ms",
                activeConnections: "1,247",
            },
            pipeline: {
                stages: [
                    { stage: "Code", status: "success", commits: 24, icon: "" },
                    { stage: "Build", status: "success", successRate: "98%", icon: "" },
                    { stage: "Test", status: "warning", coverage: "87%", icon: "" },
                    { stage: "Deploy", status: "success", deployments: 3, icon: "" },
                ],
                upcomingReleases: [
                    { version: "v2.1.0", features: ["AI Matching v2", "Real-time Tracking", "Performance Boost"], eta: "2 weeks" },
                    { version: "v2.2.0", features: ["Mobile App", "Voice Commands"], eta: "6 weeks" },
                ],
            },
            techDebt: {
                totalPoints: 34,
                criticalItems: ["Legacy Auth System", "Monolithic API Refactor", "Database Migration"],
                resolutionPlan: "Q2 2024",
            },
            security: {
                activeThreats: 0,
                blockedAttacks: 124,
                lastIncident: "7 days ago",
                compliance: {
                    gdpr: "Compliant",
                    hipaa: "In Progress",
                    soc2: "Compliant",
                    iso27001: "Pending",
                },
            },
        });
        setLastUpdate(new Date());
    };

    // Execute action
    const executeAction = async (action) => {
        if (isPreview) return;
        setLoading(true);
        try {
            let endpoint = "";
            const baseURL = API_ROOT;

            // Map action names to endpoints
            switch (action) {
                case "performance_profile":
                    endpoint = `${baseURL}/api/v1/system/actions/performance-profile`;
                    break;
                case "database_query":
                    endpoint = `${baseURL}/api/v1/system/actions/query-analyzer`;
                    break;
                case "log_analyzer":
                    endpoint = `${baseURL}/api/v1/system/actions/log-explorer`;
                    break;
                case "clear_cache":
                    endpoint = `${baseURL}/api/v1/system/actions/clear-cache`;
                    break;
                case "deploy_latest":
                    endpoint = `${baseURL}/api/v1/system/actions/deploy-latest`;
                    break;
                case "health_check":
                    endpoint = `${baseURL}/api/v1/system/actions/health-check`;
                    break;
                default:
                    endpoint = `${baseURL}/api/v1/ai/bots/available/${BOT_KEY}/run`;
            }

            console.log(`📤 Executing action '${action}' at:`, endpoint);

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: action,
                    context: {},
                    meta: { source: "devmaintenance_control_panel" },
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ Action '${action}' completed:`, data);
            await loadPanelData();
        } catch (err) {
            console.error("❌ Action failed:", err);
            alert(`Failed to execute action: ${err.message}`);
        } finally {
            setLoading(false);
            setConfirmAction(null);
        }
    };

    // Handle emergency control with confirmation
    const handleEmergencyControl = (control) => {
        setConfirmAction(control);
    };

    return (
        <div className="min-h-screen space-y-4">
            {/* Confirmation Modal */}
            {confirmAction && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
                    <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900 p-6">
                        <h3 className="flex items-center gap-2 text-lg font-bold text-white">
                            <span></span> Confirm Emergency Action
                        </h3>
                        <p className="mt-2 text-sm text-slate-400">
                            Are you sure you want to execute <span className="font-semibold text-white">{confirmAction.label}</span>?
                            This action requires authorization.
                        </p>
                        <div className="mt-4 flex justify-end gap-3">
                            <button
                                onClick={() => setConfirmAction(null)}
                                className="rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/20"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => executeAction(confirmAction.control)}
                                className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-500"
                            >
                                Confirm & Execute
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Control Panel Header */}
            <header className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800/50 via-slate-900/90 to-cyan-900/30 p-5 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    {/* Title Section */}
                    <div className="flex items-center gap-4">
                        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 text-4xl shadow-lg shadow-cyan-500/30">

                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">
                                MAINTENANCE DEV COMMAND
                            </h1>
                            <p className="text-sm text-slate-400">
                                Maintenance Dev Control Center
                            </p>
                        </div>
                    </div>

                    {/* Status & Controls */}
                    <div className="flex items-center gap-3">
                        <ConnectionStatus connected={connected} />
                        {!connected && (
                            <button
                                onClick={handleConnectAPIs}
                                disabled={isPreview}
                                className="flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-cyan-500/30 transition hover:bg-cyan-500 disabled:opacity-50"
                            >
                                Connect Monitoring
                            </button>
                        )}
                        <button
                            onClick={loadPanelData}
                            disabled={loading || isPreview}
                            className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:opacity-50"
                        >
                            <span className={loading ? "animate-spin" : ""}></span>
                        </button>
                    </div>
                </div>

                {/* System Health Status */}
                <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <HealthCard
                        component="API Gateway"
                        status={panelData.systemHealth.apiGateway.status}
                        metric={panelData.systemHealth.apiGateway.latency}
                        metricLabel="Latency"
                    />
                    <HealthCard
                        component="Database"
                        status={panelData.systemHealth.database.status}
                        metric={panelData.systemHealth.database.usage}
                        metricLabel="Usage"
                    />
                    <HealthCard
                        component="Cache"
                        status={panelData.systemHealth.cache.status}
                        metric={panelData.systemHealth.cache.hitRate}
                        metricLabel="Hit Rate"
                    />
                    <HealthCard
                        component="Message Queue"
                        status={panelData.systemHealth.messageQueue.status}
                        metric={panelData.systemHealth.messageQueue.backlog}
                        metricLabel="Backlog"
                    />
                </div>

                {/* Emergency Controls */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {EMERGENCY_CONTROLS.map((ctrl) => (
                        <EmergencyButton
                            key={ctrl.control}
                            control={ctrl}
                            onClick={() => handleEmergencyControl(ctrl)}
                            disabled={isPreview}
                        />
                    ))}
                </div>
            </header>

            {/* Preview Banner */}
            {isPreview && (
                <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="text-amber-400"></span>
                        <span className="text-sm font-semibold text-amber-100">
                            Preview Mode - Monitoring not connected
                        </span>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            <div className="flex gap-4">
                {/* Tab Navigation */}
                <nav className="hidden w-56 flex-shrink-0 space-y-1 lg:block">
                    {CONTROL_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition ${activeTab === tab.id
                                ? "bg-cyan-600/30 text-white"
                                : "text-slate-400 hover:bg-white/5 hover:text-slate-300"
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
                            className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${activeTab === tab.id
                                ? "bg-cyan-600/30 text-white"
                                : "bg-white/5 text-slate-400"
                                }`}
                        >
                            <span>{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <main className="flex-1 space-y-4">
                    {activeTab === "infrastructure" && (
                        <InfrastructureTab panelData={panelData} scalingPolicies={SCALING_POLICIES} />
                    )}
                    {activeTab === "development" && (
                        <DevelopmentTab panelData={panelData} />
                    )}
                    {activeTab === "security" && (
                        <SecurityTab panelData={panelData} />
                    )}
                    {activeTab === "diagnostics" && (
                        <DiagnosticsTab
                            scripts={automationScripts}
                            logs={systemLogs}
                            onRunScript={executeAction}
                            disabled={isPreview}
                        />
                    )}
                </main>

                {/* Engineer Tools Sidebar */}
                <aside className="hidden w-64 flex-shrink-0 space-y-4 xl:block">
                    {/* Diagnostics */}
                    <SidebarSection title="DIAGNOSTICS">
                        <SidebarButton icon="" label="Performance Profiler" onClick={() => executeAction("performance_profile")} />
                        <SidebarButton icon="" label="Query Analyzer" onClick={() => executeAction("database_query")} />
                        <SidebarButton icon="" label="Log Explorer" onClick={() => executeAction("log_analyzer")} />
                    </SidebarSection>

                    {/* Quick Actions */}
                    <SidebarSection title="QUICK ACTIONS">
                        <SidebarButton icon="" label="Clear Cache" onClick={() => executeAction("clear_cache")} />
                        <SidebarButton icon="" label="Deploy Latest" onClick={() => executeAction("deploy_latest")} />
                        <SidebarButton icon="" label="Run Health Check" onClick={() => executeAction("health_check")} />
                    </SidebarSection>

                    {/* System Metrics */}
                    <SidebarSection title="LIVE METRICS">
                        <SidebarMetric label="Uptime" value={panelData.systemMetrics.uptime} color="green" />
                        <SidebarMetric label="Error Rate" value={panelData.systemMetrics.errorRate} color="green" />
                        <SidebarMetric label="Response Time" value={panelData.systemMetrics.responseTime} color="blue" />
                        <SidebarMetric label="Connections" value={panelData.systemMetrics.activeConnections} color="purple" />
                    </SidebarSection>
                </aside>
            </div>

            {/* Status Bar Footer */}
            <footer className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4 text-xs">
                    <div className="flex flex-wrap gap-6">
                        <FooterStat label="Last Update" value={lastUpdate?.toLocaleTimeString() || "Never"} />
                        <FooterStat label="System Status" value={connected ? " All Systems Go" : " Disconnected"} />
                        <FooterStat label="Active Instances" value={`${panelData.infrastructure.autoScaling.currentInstances}/${panelData.infrastructure.autoScaling.maxInstances}`} />
                        <FooterStat label="Security" value={`${panelData.security.activeThreats} threats`} />
                    </div>
                    <Link
                        to="/ai-bots/control?bot=maintenance_dev"
                        className="text-cyan-400 hover:text-cyan-300"
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
        <div
            className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold ${connected
                ? "bg-emerald-500/20 text-emerald-300"
                : "bg-slate-500/20 text-slate-400"
                }`}
        >
            <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500 animate-pulse" : "bg-slate-500"}`} />
            {connected ? " SYSTEMS ONLINE" : " OFFLINE"}
        </div>
    );
}

function HealthCard({ component, status, metric, metricLabel }) {
    const statusConfig = {
        healthy: { color: "bg-emerald-500", icon: "", bgColor: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30" },
        warning: { color: "bg-amber-500", icon: "", bgColor: "from-amber-500/20 to-amber-600/10 border-amber-500/30" },
        critical: { color: "bg-rose-500", icon: "", bgColor: "from-rose-500/20 to-rose-600/10 border-rose-500/30" },
        unknown: { color: "bg-slate-500", icon: "", bgColor: "from-slate-500/20 to-slate-600/10 border-slate-500/30" },
    };

    const config = statusConfig[status] || statusConfig.unknown;

    return (
        <div className={`rounded-lg border bg-gradient-to-br p-3 ${config.bgColor}`}>
            <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{component}</span>
                <span>{config.icon}</span>
            </div>
            <div className="mt-2">
                <span className="text-lg font-bold text-white">{metric}</span>
                <span className="ml-1 text-xs text-slate-500">{metricLabel}</span>
            </div>
        </div>
    );
}

function EmergencyButton({ control, onClick, disabled }) {
    // Glassmorphism color variants (semi-transparent gradients + subtle borders)
    const colorClasses = {
        amber:
            "bg-gradient-to-br from-amber-400/20 to-amber-600/20 hover:from-amber-400/30 hover:to-amber-600/30 border-amber-300/30 shadow-amber-500/20",
        purple:
            "bg-gradient-to-br from-purple-400/20 to-purple-700/20 hover:from-purple-400/30 hover:to-purple-700/30 border-purple-300/30 shadow-purple-500/20",
        blue:
            "bg-gradient-to-br from-sky-400/20 to-blue-700/20 hover:from-sky-400/30 hover:to-blue-700/30 border-sky-300/30 shadow-sky-500/20",
        red:
            "bg-gradient-to-br from-rose-400/20 to-rose-700/20 hover:from-rose-400/30 hover:to-rose-700/30 border-rose-300/30 shadow-rose-500/20",
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`relative flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold text-white shadow-lg backdrop-blur-md transition disabled:opacity-50 ${colorClasses[control.color]}`}
        >
            {control.label}
            {control.requiresAuth && <span className="ml-1 text-xs opacity-70"></span>}
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

function SidebarMetric({ label, value, color }) {
    const colorClasses = {
        green: "text-emerald-400",
        blue: "text-blue-400",
        purple: "text-purple-400",
        amber: "text-amber-400",
    };

    return (
        <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
            <span className="text-sm text-slate-400">{label}</span>
            <span className={`font-semibold ${colorClasses[color]}`}>{value}</span>
        </div>
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

function InfrastructureTab({ panelData, scalingPolicies }) {
    return (
        <div className="space-y-4">
            {/* Server Status */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Server Infrastructure
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Server</th>
                                <th className="pb-3 pr-4">Region</th>
                                <th className="pb-3 pr-4 text-center">CPU</th>
                                <th className="pb-3 pr-4 text-center">Memory</th>
                                <th className="pb-3 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {panelData.infrastructure.servers.length > 0 ? (
                                panelData.infrastructure.servers.map((server) => (
                                    <tr key={server.name} className="text-slate-300">
                                        <td className="py-3 pr-4 font-mono text-cyan-400">{server.name}</td>
                                        <td className="py-3 pr-4 text-slate-400">{server.region}</td>
                                        <td className="py-3 pr-4 text-center">
                                            <UsageBar value={parseInt(server.cpu)} />
                                        </td>
                                        <td className="py-3 pr-4 text-center">
                                            <UsageBar value={parseInt(server.memory)} />
                                        </td>
                                        <td className="py-3 text-center">
                                            <span className={`rounded-full px-2 py-1 text-xs ${server.status === "Healthy"
                                                ? "bg-emerald-500/20 text-emerald-300"
                                                : "bg-amber-500/20 text-amber-300"
                                                }`}>
                                                {server.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-slate-500">
                                        Connect to view server infrastructure
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Auto-scaling */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
                        <span></span> Auto-Scaling Configuration
                    </h3>
                    <div className="text-sm text-slate-400">
                        Instances: <span className="font-bold text-white">
                            {panelData.infrastructure.autoScaling.currentInstances}
                        </span> / {panelData.infrastructure.autoScaling.maxInstances}
                    </div>
                </div>
                <div className="space-y-2">
                    {scalingPolicies.map((policy, i) => (
                        <div
                            key={i}
                            className={`flex items-center justify-between rounded-lg p-3 ${policy.active ? "bg-emerald-500/10" : "bg-white/5"
                                }`}
                        >
                            <div className="flex items-center gap-3">
                                <span className={`h-2 w-2 rounded-full ${policy.active ? "bg-emerald-500" : "bg-slate-500"}`} />
                                <span className="text-sm text-slate-300">{policy.metric}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="text-sm text-slate-400">{policy.action}</span>
                                <span className={`rounded px-2 py-0.5 text-xs ${policy.active ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-500/20 text-slate-400"
                                    }`}>
                                    {policy.active ? "Active" : "Inactive"}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function UsageBar({ value }) {
    const color = value > 80 ? "bg-rose-500" : value > 60 ? "bg-amber-500" : "bg-emerald-500";
    return (
        <div className="flex items-center gap-2">
            <div className="h-2 w-16 overflow-hidden rounded-full bg-white/10">
                <div className={`h-full ${color}`} style={{ width: `${value}%` }} />
            </div>
            <span className="text-xs text-slate-400">{value}%</span>
        </div>
    );
}

function DevelopmentTab({ panelData }) {
    return (
        <div className="space-y-4">
            {/* Pipeline Status */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Development Pipeline
                </h3>
                <div className="flex justify-between gap-2">
                    {panelData.pipeline.stages.length > 0 ? (
                        panelData.pipeline.stages.map((stage, i) => (
                            <div key={stage.stage} className="flex-1 text-center">
                                <div className={`mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full ${stage.status === "success"
                                    ? "bg-emerald-500/20"
                                    : stage.status === "warning"
                                        ? "bg-amber-500/20"
                                        : "bg-rose-500/20"
                                    }`}>
                                    <span className="text-2xl">{stage.icon}</span>
                                </div>
                                <div className="text-sm font-semibold text-white">{stage.stage}</div>
                                <div className={`text-xs ${stage.status === "success"
                                    ? "text-emerald-400"
                                    : stage.status === "warning"
                                        ? "text-amber-400"
                                        : "text-rose-400"
                                    }`}>
                                    {stage.commits && `${stage.commits} commits`}
                                    {stage.successRate && stage.successRate}
                                    {stage.coverage && stage.coverage}
                                    {stage.deployments && `${stage.deployments} deploys`}
                                </div>
                                {i < panelData.pipeline.stages.length - 1 && (
                                    <div className="absolute right-0 top-1/2 hidden h-0.5 w-8 -translate-y-1/2 bg-white/20 lg:block" />
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="flex-1 py-8 text-center text-slate-500">
                            Connect to view pipeline status
                        </div>
                    )}
                </div>
            </div>

            {/* Upcoming Releases */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Upcoming Releases
                </h3>
                <div className="space-y-3">
                    {panelData.pipeline.upcomingReleases.length > 0 ? (
                        panelData.pipeline.upcomingReleases.map((release) => (
                            <div key={release.version} className="rounded-lg border border-white/10 bg-white/5 p-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <span className="rounded bg-cyan-500/20 px-2 py-1 font-mono text-sm text-cyan-400">
                                            {release.version}
                                        </span>
                                        <span className="text-sm text-slate-400">ETA: {release.eta}</span>
                                    </div>
                                </div>
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {release.features.map((feature, i) => (
                                        <span key={i} className="rounded bg-white/10 px-2 py-1 text-xs text-slate-300">
                                            {feature}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="py-8 text-center text-slate-500">
                            No upcoming releases scheduled
                        </div>
                    )}
                </div>
            </div>

            {/* Tech Debt */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <div className="mb-4 flex items-center justify-between">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
                        <span></span> Tech Debt Management
                    </h3>
                    <div className="rounded bg-rose-500/20 px-3 py-1 text-sm font-bold text-rose-400">
                        {panelData.techDebt.totalPoints} points
                    </div>
                </div>
                <div className="mb-3 text-sm text-slate-400">
                    Resolution Target: <span className="text-white">{panelData.techDebt.resolutionPlan}</span>
                </div>
                <div className="space-y-2">
                    {panelData.techDebt.criticalItems.map((item, i) => (
                        <div key={i} className="flex items-center gap-2 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">
                            <span></span>
                            {item}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function SecurityTab({ panelData }) {
    return (
        <div className="space-y-4">
            {/* Threat Detection */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Security Operations Center
                </h3>
                <div className="grid gap-4 md:grid-cols-3">
                    <div className={`rounded-lg p-4 text-center ${panelData.security.activeThreats === 0
                        ? "bg-emerald-500/10"
                        : "bg-rose-500/10"
                        }`}>
                        <div className={`text-3xl font-bold ${panelData.security.activeThreats === 0
                            ? "text-emerald-400"
                            : "text-rose-400"
                            }`}>
                            {panelData.security.activeThreats}
                        </div>
                        <div className="text-sm text-slate-400">Active Threats</div>
                    </div>
                    <div className="rounded-lg bg-blue-500/10 p-4 text-center">
                        <div className="text-3xl font-bold text-blue-400">
                            {panelData.security.blockedAttacks}
                        </div>
                        <div className="text-sm text-slate-400">Blocked Attacks</div>
                    </div>
                    <div className="rounded-lg bg-slate-500/10 p-4 text-center">
                        <div className="text-lg font-bold text-white">
                            {panelData.security.lastIncident}
                        </div>
                        <div className="text-sm text-slate-400">Last Incident</div>
                    </div>
                </div>
            </div>

            {/* Compliance Status */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Compliance Status
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                    {Object.entries(panelData.security.compliance).map(([standard, status]) => (
                        <div key={standard} className="flex items-center justify-between rounded-lg bg-white/5 p-3">
                            <span className="font-semibold uppercase text-white">{standard}</span>
                            <span className={`rounded-full px-2 py-1 text-xs ${status === "Compliant"
                                ? "bg-emerald-500/20 text-emerald-300"
                                : status === "In Progress"
                                    ? "bg-amber-500/20 text-amber-300"
                                    : "bg-slate-500/20 text-slate-400"
                                }`}>
                                {status}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function DiagnosticsTab({ scripts, logs, onRunScript, disabled }) {
    return (
        <div className="space-y-4">
            {/* Automation Scripts */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Automation Scripts
                </h3>
                <div className="space-y-3">
                    {scripts && scripts.length > 0 ? (
                        scripts.map((script) => (
                            <div
                                key={script.script}
                                className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 p-4"
                            >
                                <div>
                                    <div className="font-semibold text-white">{script.label}</div>
                                    <div className="mt-1 text-sm text-slate-400">
                                        Runs: {script.frequency}  Last: {script.lastRun}
                                    </div>
                                </div>
                                <button
                                    onClick={() => onRunScript(script.script)}
                                    disabled={disabled}
                                    className="rounded-lg bg-cyan-600/80 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-500 disabled:opacity-50"
                                >
                                    Run Now
                                </button>
                            </div>
                        ))
                    ) : (
                        <div className="text-center text-slate-400">Loading scripts...</div>
                    )}
                </div>
            </div>

            {/* System Logs */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Recent System Logs
                </h3>
                <div className="space-y-2 font-mono text-xs">
                    {logs && logs.length > 0 ? (
                        logs.map((log, idx) => (
                            <LogEntry key={idx} time={log.time} level={log.level} message={log.message} />
                        ))
                    ) : (
                        <div className="text-center text-slate-400">Loading logs...</div>
                    )}
                </div>
            </div>
        </div>
    );
}

function LogEntry({ time, level, message }) {
    const levelColors = {
        INFO: "text-blue-400",
        WARN: "text-amber-400",
        ERROR: "text-rose-400",
    };

    return (
        <div className="flex gap-3 rounded bg-black/30 px-3 py-2 text-slate-300">
            <span className="text-slate-500">{time}</span>
            <span className={`font-semibold ${levelColors[level]}`}>[{level}]</span>
            <span>{message}</span>
        </div>
    );
}
