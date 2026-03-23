/**
 *  GIT - Executive Intelligence Control Panel
 * Strategic management command center for GTS Logistics
 */
import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "executive_intelligence";

// Tab definitions
const CONTROL_TABS = [
    { id: "strategic_dashboard", name: "Strategic Dashboard", icon: "" },
    { id: "predictive_insights", name: "Predictive Insights", icon: "" },
    { id: "decision_panel", name: "Decision Panel", icon: "" },
    { id: "market_intelligence", name: "Market Intel", icon: "" },
];

// Strategic alerts
const STRATEGIC_ALERTS = [
    { type: "opportunity", icon: "", message: "Market expansion opportunity detected in Western Canada" },
    { type: "warning", icon: "", message: "Competitor pricing shift detected - 8% reduction" },
    { type: "info", icon: "", message: "Q4 revenue target 86% achieved" },
];

// Competitors data
const COMPETITORS = [
    { name: "FreightCompass", marketShare: "32%", trend: "Stable", threat: "Medium" },
    { name: "LoadLink", marketShare: "28%", trend: "Declining", threat: "Low" },
    { name: "TransCore", marketShare: "15%", trend: "Growing", threat: "High" },
];

// Industry trends
const INDUSTRY_TRENDS = [
    "Digital freight brokerage growing at 15% annually",
    "Demand for cross-border shipping up 22%",
    "EV fleet adoption accelerating in logistics",
    "AI-powered route optimization becoming standard",
];

export default function ExecutiveIntelligenceControlPanel({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeTab, setActiveTab] = useState("strategic_dashboard");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Control panel data state
    const [panelData, setPanelData] = useState({
        // Company metrics
        companyMetrics: {
            marketShare: { value: "0%", trend: "0%" },
            revenueGrowth: { value: "0%", trend: "0%" },
            customerSat: { value: "0%", trend: "0%" },
            opEfficiency: { value: "0%", trend: "0%" },
        },
        // KPIs
        kpis: {
            financial: [
                { name: "Revenue", current: "$0", target: "$0", progress: 0 },
                { name: "Profit Margin", current: "0%", target: "0%", progress: 0 },
            ],
            operational: [
                { name: "On-time Delivery", current: "0%", target: "0%", progress: 0 },
                { name: "Load Efficiency", current: "0%", target: "0%", progress: 0 },
            ],
        },
        // Predictions
        predictions: {
            revenueForecast: { nextMonth: "$0", nextQuarter: "$0", confidence: "0%" },
            riskAssessment: { highRisk: [], mitigations: [] },
        },
        // Approval queue
        approvalQueue: [],
        // Strategic initiatives
        initiatives: [],
    });

    // Load data from API
    const loadPanelData = useCallback(async () => {
        if (isPreview) return;
        setLoading(true);
        try {
        const [statusRes, kpisRes] = await Promise.all([
            axiosClient.get(`/api/v1/ai/bots/${BOT_KEY}/status`).catch(() => null),
            axiosClient.get(`/api/v1/ai/bots/${BOT_KEY}/kpis`).catch(() => null),
        ]);

            if (statusRes?.data || kpisRes?.data) {
                setConnected(true);
                // Update with real data when available
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
            companyMetrics: {
                marketShare: { value: "18.4%", trend: " 2.3%" },
                revenueGrowth: { value: "24.7%", trend: " 4.1%" },
                customerSat: { value: "92%", trend: " 3%" },
                opEfficiency: { value: "87%", trend: " 1.5%" },
            },
            kpis: {
                financial: [
                    { name: "Revenue", current: "$2.4M", target: "$2.8M", progress: 86 },
                    { name: "Profit Margin", current: "28%", target: "30%", progress: 93 },
                    { name: "Cost Reduction", current: "12%", target: "15%", progress: 80 },
                ],
                operational: [
                    { name: "On-time Delivery", current: "94%", target: "95%", progress: 99 },
                    { name: "Load Efficiency", current: "87%", target: "90%", progress: 97 },
                    { name: "Customer Retention", current: "91%", target: "95%", progress: 96 },
                ],
            },
            predictions: {
                revenueForecast: { nextMonth: "$2.6M", nextQuarter: "$8.1M", confidence: "89%" },
                riskAssessment: {
                    highRisk: ["Fuel price volatility", "Labor shortage", "Seasonal demand fluctuation"],
                    mitigations: ["Fuel hedging contracts", "Carrier retention program", "Dynamic pricing model"],
                },
            },
            approvalQueue: [
                { item: "New Carrier Agreement - TransWest", type: "Contract", priority: "High", value: "$450K" },
                { item: "Technology Investment - AI Platform", type: "Budget", priority: "Medium", value: "$125K" },
                { item: "Fleet Expansion - 15 Units", type: "CapEx", priority: "High", value: "$2.1M" },
            ],
            initiatives: [
                { name: "Digital Transformation", status: "In Progress", progress: 65, eta: "Q2 2024" },
                { name: "Market Expansion - Western Canada", status: "Planning", progress: 30, eta: "Q3 2024" },
                { name: "AI-Powered Operations", status: "In Progress", progress: 78, eta: "Q1 2024" },
            ],
        });
        setLastUpdate(new Date());
    };

    // Execute action
    const executeAction = async (action) => {
        if (isPreview) return;
        try {
            await axiosClient.post(`/api/v1/bots/${BOT_KEY}/run`, {
                message: action,
                context: {},
                meta: { source: "executive_control_panel" },
            });
            await loadPanelData();
        } catch (err) {
            console.error("Action failed:", err);
        }
    };

    return (
        <div className="min-h-screen space-y-4">
            {/* Control Panel Header */}
            <header className="rounded-2xl border border-white/10 bg-gradient-to-br from-amber-900/30 via-slate-900/90 to-purple-900/30 p-5 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    {/* Title Section */}
                    <div className="flex items-center gap-4">
                        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-4xl shadow-lg shadow-amber-500/30">

                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">
                                EXECUTIVE COMMAND CENTER
                            </h1>
                            <p className="text-sm text-slate-400">
                                GIT Strategic Intelligence Control
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
                                className="flex items-center gap-2 rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-amber-500/30 transition hover:bg-amber-500 disabled:opacity-50"
                            >
                                Connect Analytics
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

                {/* Company Metrics */}
                <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <MetricCard
                        label="Market Share"
                        value={panelData.companyMetrics.marketShare.value}
                        trend={panelData.companyMetrics.marketShare.trend}
                        color="blue"
                    />
                    <MetricCard
                        label="Revenue Growth"
                        value={panelData.companyMetrics.revenueGrowth.value}
                        trend={panelData.companyMetrics.revenueGrowth.trend}
                        color="green"
                    />
                    <MetricCard
                        label="Customer Satisfaction"
                        value={panelData.companyMetrics.customerSat.value}
                        trend={panelData.companyMetrics.customerSat.trend}
                        color="amber"
                    />
                    <MetricCard
                        label="Op. Efficiency"
                        value={panelData.companyMetrics.opEfficiency.value}
                        trend={panelData.companyMetrics.opEfficiency.trend}
                        color="purple"
                    />
                </div>

                {/* Strategic Alerts */}
                <div className="mt-4 space-y-2">
                    {STRATEGIC_ALERTS.map((alert, i) => (
                        <div
                            key={i}
                            className={`flex items-center gap-3 rounded-lg px-4 py-2 ${alert.type === "opportunity"
                                ? "bg-emerald-500/10 text-emerald-300"
                                : alert.type === "warning"
                                    ? "bg-amber-500/10 text-amber-300"
                                    : "bg-blue-500/10 text-blue-300"
                                }`}
                        >
                            <span>{alert.icon}</span>
                            <span className="text-sm">{alert.message}</span>
                        </div>
                    ))}
                </div>
            </header>

            {/* Preview Banner */}
            {isPreview && (
                <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="text-amber-400"></span>
                        <span className="text-sm font-semibold text-amber-100">
                            Preview Mode - Analytics not active
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
                                ? "bg-amber-600/30 text-white"
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
                                ? "bg-amber-600/30 text-white"
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
                    {activeTab === "strategic_dashboard" && (
                        <StrategicDashboardTab panelData={panelData} />
                    )}
                    {activeTab === "predictive_insights" && (
                        <PredictiveInsightsTab panelData={panelData} />
                    )}
                    {activeTab === "decision_panel" && (
                        <DecisionPanelTab
                            panelData={panelData}
                            onAction={executeAction}
                            disabled={isPreview}
                        />
                    )}
                    {activeTab === "market_intelligence" && (
                        <MarketIntelligenceTab competitors={COMPETITORS} trends={INDUSTRY_TRENDS} />
                    )}
                </main>

                {/* Decision Sidebar */}
                <aside className="hidden w-64 flex-shrink-0 space-y-4 xl:block">
                    {/* Quick Analysis */}
                    <SidebarSection title="QUICK ANALYSIS">
                        <SidebarButton icon="" label="Generate Report" onClick={() => executeAction("generate_report")} />
                        <SidebarButton icon="" label="Deep Analysis" onClick={() => executeAction("deep_analysis")} />
                        <SidebarButton icon="" label="Trend Forecast" onClick={() => executeAction("trend_forecast")} />
                    </SidebarSection>

                    {/* Executive Actions */}
                    <SidebarSection title="EXECUTIVE ACTIONS">
                        <SidebarButton icon="" label="Board Briefing" onClick={() => executeAction("board_briefing")} />
                        <SidebarButton icon="" label="Set Targets" onClick={() => executeAction("set_targets")} />
                        <SidebarButton icon="" label="Quick Decision" onClick={() => executeAction("quick_decision")} />
                    </SidebarSection>

                    {/* System Status */}
                    <SidebarSection title="SYSTEM STATUS">
                        <SidebarStatus icon="" label="Analytics API" status={connected ? "Connected" : "Offline"} color={connected ? "green" : "red"} />
                        <SidebarStatus icon="" label="AI Engine" status="Active" color="green" />
                        <SidebarStatus icon="" label="Data Feed" status="Real-time" color="blue" />
                    </SidebarSection>
                </aside>
            </div>

            {/* Status Bar Footer */}
            <footer className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4 text-xs">
                    <div className="flex flex-wrap gap-6">
                        <FooterStat label="Last Update" value={lastUpdate?.toLocaleTimeString() || "Never"} />
                        <FooterStat label="Data Source" value={connected ? "Live Analytics" : "No Connection"} />
                        <FooterStat label="AI Confidence" value="94%" />
                        <FooterStat label="Report Status" value="Ready" />
                    </div>
                    <Link
                        to="/ai-bots/control?bot=executive_intelligence"
                        className="text-amber-400 hover:text-amber-300"
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
            {connected ? " LIVE" : " OFFLINE"}
        </div>
    );
}

function MetricCard({ label, value, trend, color }) {
    const colorClasses = {
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
        green: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30",
        amber: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
        purple: "from-purple-500/20 to-purple-600/10 border-purple-500/30",
    };

    const trendColor = trend.startsWith("") ? "text-emerald-400" : trend.startsWith("") ? "text-rose-400" : "text-slate-400";

    return (
        <div className={`rounded-lg border bg-gradient-to-br p-3 ${colorClasses[color]}`}>
            <div className="text-xs font-medium text-slate-400">{label}</div>
            <div className="mt-1 flex items-baseline gap-2">
                <span className="text-xl font-bold text-white">{value}</span>
                <span className={`text-xs font-semibold ${trendColor}`}>{trend}</span>
            </div>
        </div>
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

function StrategicDashboardTab({ panelData }) {
    return (
        <div className="space-y-4">
            {/* Financial KPIs */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Financial KPIs
                </h3>
                <div className="space-y-4">
                    {panelData.kpis.financial.map((kpi) => (
                        <KPIRow key={kpi.name} kpi={kpi} />
                    ))}
                </div>
            </div>

            {/* Operational KPIs */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Operational KPIs
                </h3>
                <div className="space-y-4">
                    {panelData.kpis.operational.map((kpi) => (
                        <KPIRow key={kpi.name} kpi={kpi} />
                    ))}
                </div>
            </div>

            {/* Strategic Initiatives */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Strategic Initiatives
                </h3>
                <div className="space-y-3">
                    {panelData.initiatives.length > 0 ? (
                        panelData.initiatives.map((init, i) => (
                            <div key={i} className="rounded-lg bg-white/5 p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="font-semibold text-white">{init.name}</div>
                                        <div className="text-sm text-slate-400">
                                            {init.status}  ETA: {init.eta}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-bold text-amber-400">{init.progress}%</div>
                                    </div>
                                </div>
                                <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                                    <div
                                        className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500"
                                        style={{ width: `${init.progress}%` }}
                                    />
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="py-8 text-center text-slate-500">
                            Connect Analytics to view initiatives
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function KPIRow({ kpi }) {
    const progressColor =
        kpi.progress >= 90
            ? "from-emerald-500 to-green-500"
            : kpi.progress >= 70
                ? "from-amber-500 to-orange-500"
                : "from-rose-500 to-red-500";

    return (
        <div>
            <div className="mb-2 flex items-center justify-between">
                <span className="text-sm text-slate-300">{kpi.name}</span>
                <div className="text-sm">
                    <span className="font-semibold text-white">{kpi.current}</span>
                    <span className="text-slate-500"> / {kpi.target}</span>
                </div>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
                <div
                    className={`h-full rounded-full bg-gradient-to-r ${progressColor}`}
                    style={{ width: `${kpi.progress}%` }}
                />
            </div>
            <div className="mt-1 text-right text-xs text-slate-500">{kpi.progress}%</div>
        </div>
    );
}

function PredictiveInsightsTab({ panelData }) {
    return (
        <div className="space-y-4">
            {/* Revenue Forecast */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Revenue Forecast
                </h3>
                <div className="grid gap-4 md:grid-cols-3">
                    <div className="rounded-lg bg-emerald-500/10 p-4 text-center">
                        <div className="text-xs text-slate-400">Next Month</div>
                        <div className="mt-1 text-2xl font-bold text-emerald-400">
                            {panelData.predictions.revenueForecast.nextMonth}
                        </div>
                    </div>
                    <div className="rounded-lg bg-blue-500/10 p-4 text-center">
                        <div className="text-xs text-slate-400">Next Quarter</div>
                        <div className="mt-1 text-2xl font-bold text-blue-400">
                            {panelData.predictions.revenueForecast.nextQuarter}
                        </div>
                    </div>
                    <div className="rounded-lg bg-purple-500/10 p-4 text-center">
                        <div className="text-xs text-slate-400">Confidence Level</div>
                        <div className="mt-1 text-2xl font-bold text-purple-400">
                            {panelData.predictions.revenueForecast.confidence}
                        </div>
                    </div>
                </div>
            </div>

            {/* Risk Assessment */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Risk Assessment
                </h3>
                <div className="grid gap-4 md:grid-cols-2">
                    <div>
                        <h4 className="mb-3 text-sm font-semibold text-rose-400">High Risk Factors</h4>
                        <div className="space-y-2">
                            {panelData.predictions.riskAssessment.highRisk.length > 0 ? (
                                panelData.predictions.riskAssessment.highRisk.map((risk, i) => (
                                    <div key={i} className="flex items-center gap-2 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">
                                        <span></span>
                                        {risk}
                                    </div>
                                ))
                            ) : (
                                <div className="text-sm text-slate-500 italic">No high risk factors identified</div>
                            )}
                        </div>
                    </div>
                    <div>
                        <h4 className="mb-3 text-sm font-semibold text-emerald-400">Recommended Mitigations</h4>
                        <div className="space-y-2">
                            {panelData.predictions.riskAssessment.mitigations.length > 0 ? (
                                panelData.predictions.riskAssessment.mitigations.map((mitigation, i) => (
                                    <div key={i} className="flex items-center gap-2 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm text-emerald-300">
                                        <span></span>
                                        {mitigation}
                                    </div>
                                ))
                            ) : (
                                <div className="text-sm text-slate-500 italic">No mitigations available</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Scenario Analysis */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Scenario Analysis
                </h3>
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="font-semibold text-white">Market Expansion - Western Canada</div>
                            <div className="text-sm text-slate-400">
                                Strategic opportunity with high growth potential
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-xl font-bold text-emerald-400">+35%</div>
                            <div className="text-xs text-slate-400">Revenue Potential</div>
                        </div>
                    </div>
                    <div className="mt-3 border-t border-white/10 pt-3">
                        <div className="text-xs text-slate-500">Requirements:</div>
                        <div className="mt-1 flex flex-wrap gap-2">
                            <span className="rounded bg-white/10 px-2 py-1 text-xs text-slate-300">
                                $500K Investment
                            </span>
                            <span className="rounded bg-white/10 px-2 py-1 text-xs text-slate-300">
                                6 New Hires
                            </span>
                            <span className="rounded bg-white/10 px-2 py-1 text-xs text-slate-300">
                                Q2 Timeline
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function DecisionPanelTab({ panelData, onAction, disabled }) {
    return (
        <div className="space-y-4">
            {/* Approval Queue */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Approval Queue
                </h3>
                <div className="space-y-3">
                    {panelData.approvalQueue.length > 0 ? (
                        panelData.approvalQueue.map((item, i) => (
                            <div key={i} className="rounded-lg border border-white/10 bg-white/5 p-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <div className="font-semibold text-white">{item.item}</div>
                                        <div className="mt-1 flex gap-2">
                                            <span className="rounded bg-blue-500/20 px-2 py-0.5 text-xs text-blue-300">
                                                {item.type}
                                            </span>
                                            <span className={`rounded px-2 py-0.5 text-xs ${item.priority === "High"
                                                ? "bg-rose-500/20 text-rose-300"
                                                : "bg-amber-500/20 text-amber-300"
                                                }`}>
                                                {item.priority} Priority
                                            </span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-lg font-bold text-emerald-400">{item.value}</div>
                                        <div className="mt-2 flex gap-2">
                                            <button
                                                onClick={() => onAction(`approve_${item.type.toLowerCase()}`)}
                                                disabled={disabled}
                                                className="rounded bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
                                            >
                                                Approve
                                            </button>
                                            <button
                                                onClick={() => onAction(`reject_${item.type.toLowerCase()}`)}
                                                disabled={disabled}
                                                className="rounded bg-rose-600 px-3 py-1 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
                                            >
                                                Reject
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="py-8 text-center text-slate-500">
                            No items pending approval
                        </div>
                    )}
                </div>
            </div>

            {/* Quick Decisions */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Quick Decisions
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                    <button
                        onClick={() => onAction("emergency_meeting")}
                        disabled={disabled}
                        className="flex items-center gap-3 rounded-lg bg-rose-600/80 p-4 text-left transition hover:bg-rose-500 disabled:opacity-50"
                    >
                        <span className="text-2xl"></span>
                        <div>
                            <div className="font-semibold text-white">Emergency Meeting</div>
                            <div className="text-xs text-rose-200">Call immediate board session</div>
                        </div>
                    </button>
                    <button
                        onClick={() => onAction("budget_reallocation")}
                        disabled={disabled}
                        className="flex items-center gap-3 rounded-lg bg-amber-600/80 p-4 text-left transition hover:bg-amber-500 disabled:opacity-50"
                    >
                        <span className="text-2xl"></span>
                        <div>
                            <div className="font-semibold text-white">Budget Reallocation</div>
                            <div className="text-xs text-amber-200">Adjust quarterly budget</div>
                        </div>
                    </button>
                    <button
                        onClick={() => onAction("strategic_pivot")}
                        disabled={disabled}
                        className="flex items-center gap-3 rounded-lg bg-purple-600/80 p-4 text-left transition hover:bg-purple-500 disabled:opacity-50"
                    >
                        <span className="text-2xl"></span>
                        <div>
                            <div className="font-semibold text-white">Strategic Pivot</div>
                            <div className="text-xs text-purple-200">Review strategy direction</div>
                        </div>
                    </button>
                    <button
                        onClick={() => onAction("stakeholder_update")}
                        disabled={disabled}
                        className="flex items-center gap-3 rounded-lg bg-blue-600/80 p-4 text-left transition hover:bg-blue-500 disabled:opacity-50"
                    >
                        <span className="text-2xl"></span>
                        <div>
                            <div className="font-semibold text-white">Stakeholder Update</div>
                            <div className="text-xs text-blue-200">Send progress report</div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    );
}

function MarketIntelligenceTab({ competitors, trends }) {
    return (
        <div className="space-y-4">
            {/* Competitor Analysis */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Competitor Analysis
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Competitor</th>
                                <th className="pb-3 pr-4 text-center">Market Share</th>
                                <th className="pb-3 pr-4 text-center">Trend</th>
                                <th className="pb-3 text-center">Threat Level</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {competitors.map((comp) => (
                                <tr key={comp.name} className="text-slate-300">
                                    <td className="py-3 pr-4 font-medium">{comp.name}</td>
                                    <td className="py-3 pr-4 text-center font-semibold">{comp.marketShare}</td>
                                    <td className="py-3 pr-4 text-center">
                                        <span className={`${comp.trend === "Growing"
                                            ? "text-rose-400"
                                            : comp.trend === "Declining"
                                                ? "text-emerald-400"
                                                : "text-slate-400"
                                            }`}>
                                            {comp.trend === "Growing" ? "" : comp.trend === "Declining" ? "" : ""} {comp.trend}
                                        </span>
                                    </td>
                                    <td className="py-3 text-center">
                                        <span className={`rounded-full px-2 py-1 text-xs ${comp.threat === "High"
                                            ? "bg-rose-500/20 text-rose-300"
                                            : comp.threat === "Medium"
                                                ? "bg-amber-500/20 text-amber-300"
                                                : "bg-emerald-500/20 text-emerald-300"
                                            }`}>
                                            {comp.threat}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Industry Trends */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Industry Trends
                </h3>
                <div className="space-y-3">
                    {trends.map((trend, i) => (
                        <div key={i} className="flex items-start gap-3 rounded-lg bg-white/5 p-3">
                            <span className="text-blue-400"></span>
                            <span className="text-sm text-slate-300">{trend}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
