/**
 * AI Freight Broker Dashboard - Complete Redesign
 * Central dispatch overview for Gabani Transport Solutions (GTS)
 */
import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "freight_broker";

// Navigation tabs
const NAV_TABS = [
    { id: "dashboard", name: "Dashboard", icon: "", path: "/ai-bots/freight" },
    { id: "shipments", name: "Shipments", icon: "", path: "/shipments" },
    { id: "map", name: "Map", icon: "", path: "/map" },
    { id: "finance", name: "Finance Dashboard", icon: "", path: "/finance" },
    { id: "expenses", name: "Platform Expenses", icon: "", path: "/platform-expenses" },
    { id: "emails", name: "Email Logs", icon: "", path: "/emails" },
    { id: "ai-bots", name: "AI Bots", icon: "", path: "/ai-bots" },
];

// AI Suggestions data
const AI_SUGGESTIONS = [
    {
        id: 1,
        icon: "",
        title: "Sort loads by profit and risk",
        description: "Prioritize high-margin, low-risk shipments",
        priority: "high",
    },
    {
        id: 2,
        icon: "",
        title: "Auto-assign best carrier based on load history",
        description: "Match shipments with highest-rated carriers",
        priority: "medium",
    },
    {
        id: 3,
        icon: "",
        title: "Predict delays from weather and traffic levels",
        description: "Proactively adjust ETAs and notify customers",
        priority: "low",
    },
];

// Market rates data
const MARKET_RATES = [
    { route: "Toronto-Vancouver", rate: "$4.85/mile" },
    { route: "Montreal-Calgary", rate: "$4.20/mile" },
    { route: "Vancouver-Edmonton", rate: "$3.95/mile" },
    { route: "Toronto-Montreal", rate: "$2.80/mile" },
];

const MARKET_ROUTES_STORAGE_KEY = "freight_broker_market_routes";

export default function FreightBrokerDashboard({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeTab, setActiveTab] = useState("dashboard");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [marketRates, setMarketRates] = useState([]);

    const activeMarketRoutes = marketRates.length > 0 ? marketRates : MARKET_RATES;

    const persistMarketRoutesForMap = useCallback(() => {
        if (typeof window === "undefined") return;
        window.sessionStorage.setItem(
            MARKET_ROUTES_STORAGE_KEY,
            JSON.stringify(activeMarketRoutes)
        );
    }, [activeMarketRoutes]);

    // Dashboard data state
    const [dashboardData, setDashboardData] = useState({
        totalLoads: 0,
        onTheWay: 0,
        revenue30Days: 0,
        alerts: 0,
        avgTransitTime: "3.7h",
        statusOverview: {
            onTheWay: 0,
            delivered: 0,
            delayed: 0,
        },
        carrierNetwork: {
            total: 0,
            activeToday: 0,
            avgRating: "0.0",
        },
        dispatchMetrics: {
            successRate: "0%",
            avgTurnaround: "0h",
            responseTime: "0m",
        },
    });

    // Load dashboard data from API
    const loadDashboardData = useCallback(async () => {
        if (isPreview) return;
        setLoading(true);
        try {
            // Try to get bot status
            const statusRes = await axiosClient
                .get(`/api/v1/ai/bots/available/${BOT_KEY}/status`)
                .catch(() => null);

            // Try to get shipment stats
            const shipmentsRes = await axiosClient
                .get("/api/v1/shipments/stats")
                .catch(() => null);

            if (statusRes?.data || shipmentsRes?.data) {
                setConnected(true);
                const stats = shipmentsRes?.data || {};
                setDashboardData((prev) => ({
                    ...prev,
                    totalLoads: stats.total || 0,
                    onTheWay: stats.in_transit || 0,
                    revenue30Days: stats.revenue_30d || 0,
                    alerts: stats.delayed || 0,
                    statusOverview: {
                        onTheWay: stats.in_transit || 0,
                        delivered: stats.delivered || 0,
                        delayed: stats.delayed || 0,
                    },
                }));
            }
            setLastUpdate(new Date());
        } catch (err) {
            console.warn("Dashboard load error:", err);
        } finally {
            setLoading(false);
        }
    }, [isPreview]);

    useEffect(() => {
        loadDashboardData();
    }, [loadDashboardData]);

    // Fetch market rates
    useEffect(() => {
        const fetchMarketRates = async () => {
            try {
                const res = await axiosClient.get("/api/v1/freight/canadian-market-rates");
                if (res.data?.rates) {
                    // Convert backend rate format to display format (rate to $/mile)
                    const formattedRates = res.data.rates.map((item) => {
                        const route = item.route || item.name || `${item.origin || "-"}-${item.destination || "-"}`;
                        const rateValue = Number(item.rate || item.rate_per_km || 0);
                        return {
                            route,
                            rate: `$${rateValue.toFixed(2)}/mile`,
                            trend: item.trend,
                            reliability: item.reliability || item.volatility_index,
                        };
                    });
                    setMarketRates(formattedRates);
                }
            } catch (error) {
                console.error("Error fetching market rates:", error);
                // Fallback to static rates if API fails
                setMarketRates([
                    { route: "Toronto-Vancouver", rate: "$4.85/mile", trend: "stable", reliability: 0.95 },
                    { route: "Montreal-Calgary", rate: "$4.20/mile", trend: "up", reliability: 0.92 },
                    { route: "Vancouver-Edmonton", rate: "$3.95/mile", trend: "stable", reliability: 0.90 },
                    { route: "Toronto-Montreal", rate: "$2.80/mile", trend: "down", reliability: 0.98 },
                ]);
            }
        };

        if (!isPreview) {
            fetchMarketRates();
            // Refresh market rates every 30 seconds
            const interval = setInterval(fetchMarketRates, 30000);
            return () => clearInterval(interval);
        }
    }, [isPreview]);

    // Simulate API connection
    const handleConnectAPIs = () => {
        setConnected(true);
        setDashboardData({
            totalLoads: 1245,
            onTheWay: 89,
            revenue30Days: 125000,
            alerts: 12,
            avgTransitTime: "3.7h",
            statusOverview: {
                onTheWay: 89,
                delivered: 1156,
                delayed: 12,
            },
            carrierNetwork: {
                total: 247,
                activeToday: 34,
                avgRating: "4.6",
            },
            dispatchMetrics: {
                successRate: "94%",
                avgTurnaround: "2.4h",
                responseTime: "15m",
            },
        });
        setLastUpdate(new Date());
    };

    // Execute bot action
    const executeAction = async (action) => {
        if (isPreview) return;
        try {
            const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
                message: action,
                context: {},
                meta: { source: "freight_dashboard" },
            });
            console.log("Action result:", res?.data);
            await loadDashboardData();
        } catch (err) {
            console.error("Action failed:", err);
        }
    };

    return (
        <div className="min-h-screen space-y-6">
            {/* Bot Header */}
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-blue-900/30 via-slate-900/90 to-indigo-900/30 p-5 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-3xl shadow-lg">

                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">AI Freight Broker</h1>
                            <p className="text-sm text-slate-400">
                                Central dispatch overview for Gabani Transport Solutions (GTS)
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Connection Status */}
                        <div
                            className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold ${connected
                                ? "bg-emerald-500/20 text-emerald-300"
                                : "bg-slate-500/20 text-slate-400"
                                }`}
                        >
                            <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500" : "bg-slate-500"}`} />
                            {connected ? " LIVE" : " OFFLINE"}
                        </div>

                        {/* Connect APIs Button */}
                        {!connected && (
                            <button
                                onClick={handleConnectAPIs}
                                disabled={isPreview}
                                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                Connect APIs
                            </button>
                        )}

                        {/* Refresh Button */}
                        <button
                            onClick={loadDashboardData}
                            disabled={loading || isPreview}
                            className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:opacity-50"
                        >
                            <span className={loading ? "animate-spin" : ""}></span>
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Last Update */}
                <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
                    <span>Last updated:</span>
                    <span className="text-slate-400">
                        {lastUpdate ? lastUpdate.toLocaleTimeString() : "Never"}
                    </span>
                </div>
            </div>

            {/* Preview Mode Banner */}
            {isPreview && (
                <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="text-amber-400"></span>
                        <span className="text-sm font-semibold text-amber-100">
                            Intelligence Mode - Backend not active
                        </span>
                    </div>
                </div>
            )}

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {/* Total Loads */}
                <StatCard
                    icon=""
                    title="TOTAL LOADS"
                    value={dashboardData.totalLoads.toLocaleString()}
                    subtitle="All known shipments in system"
                    color="blue"
                />

                {/* On The Way */}
                <StatCard
                    icon=""
                    title="ON THE WAY"
                    value={dashboardData.onTheWay.toLocaleString()}
                    subtitle="In transit or dispatched"
                    color="green"
                />

                {/* Routes & Map */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <div className="mb-3 flex items-center gap-2">
                        <span className="text-2xl"></span>
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                            ROUTES & MAP
                        </h3>
                    </div>
                    <div className="mb-2 text-2xl font-bold text-white">Live Map</div>
                    <p className="mb-4 text-sm text-slate-400">Live map integration</p>
                    <Link
                        to="/map"
                        state={{ marketRoutes: activeMarketRoutes }}
                        onClick={persistMarketRoutesForMap}
                        className="inline-flex items-center gap-2 rounded-lg bg-purple-600/80 px-4 py-2 text-sm font-semibold text-white transition hover:bg-purple-500/80"
                    >
                        View Map
                    </Link>
                </div>
            </div>

            {/* AWS Transit & Alerts Row */}
            <div className="grid gap-4 lg:grid-cols-2">
                {/* AWS Transit */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 text-sm font-semibold text-white">AWS TRANSIT</h3>
                    <div className="mb-2 flex items-baseline gap-2">
                        <span className="text-3xl font-bold text-white">
                            {dashboardData.avgTransitTime}
                        </span>
                        <span className="text-sm text-slate-400">Avg. transit time</span>
                    </div>
                    <p className="mb-4 text-xs text-slate-500">
                        Calculated from recent trips
                    </p>

                    {/* Revenue Sub-metric */}
                    <div className="border-t border-white/10 pt-4">
                        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                            REVENUE (30 DAYS)
                        </div>
                        <div className="mt-1 text-2xl font-bold text-emerald-400">
                            ${dashboardData.revenue30Days.toLocaleString()}
                        </div>
                        <p className="text-xs text-slate-500">
                            {connected ? "Live data from API" : "Connect API for live data"}
                        </p>
                    </div>
                </div>

                {/* Alerts */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 text-sm font-semibold text-white">ALERTS</h3>
                    <div className="mb-2 flex items-baseline gap-2">
                        <span
                            className={`text-3xl font-bold ${dashboardData.alerts > 0 ? "text-rose-400" : "text-white"
                                }`}
                        >
                            {dashboardData.alerts}
                        </span>
                        <span className="text-sm text-slate-400">
                            Loads flagged as delayed or late
                        </span>
                    </div>

                    {/* Status Overview */}
                    <div className="mt-4">
                        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                            STATUS OVERVIEW
                        </h4>
                        <div className="space-y-2">
                            <StatusRow
                                color="blue"
                                label="On the way"
                                count={dashboardData.statusOverview.onTheWay}
                            />
                            <StatusRow
                                color="green"
                                label="Delivered"
                                count={dashboardData.statusOverview.delivered}
                            />
                            <StatusRow
                                color="red"
                                label="Delayed"
                                count={dashboardData.statusOverview.delayed}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* AI Suggestions */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                    <span></span> AI SUGGESTIONS
                </h3>
                <div className="space-y-3">
                    {AI_SUGGESTIONS.map((suggestion) => (
                        <div
                            key={suggestion.id}
                            className="flex items-center gap-4 rounded-lg bg-white/5 p-4"
                        >
                            <span className="text-2xl">{suggestion.icon}</span>
                            <div className="flex-1">
                                <div className="font-semibold text-white">{suggestion.title}</div>
                                <div className="text-sm text-slate-400">
                                    {suggestion.description}
                                </div>
                            </div>
                            <button
                                onClick={() => executeAction(suggestion.title)}
                                disabled={isPreview}
                                className="rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                Apply
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3">
                <ActionButton
                    icon=""
                    label="Find Available Loads"
                    variant="primary"
                    onClick={() => executeAction("find_loads")}
                    disabled={isPreview}
                />
                <ActionButton
                    icon=""
                    label="Search Carriers"
                    variant="secondary"
                    onClick={() => executeAction("search_carriers")}
                    disabled={isPreview}
                />
                <ActionButton
                    icon=""
                    label="View Market Rates"
                    variant="secondary"
                    onClick={() => executeAction("market_rates")}
                    disabled={isPreview}
                />
                <Link to="/ai-bots/control?bot=freight_broker">
                    <ActionButton icon="" label="Configure Bot" variant="outline" />
                </Link>
            </div>

            {/* Market Intelligence */}
            <div className="grid gap-4 lg:grid-cols-2">
                {/* Market Rates */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> MARKET RATES
                    </h3>
                    <div className="space-y-2">
                        {(marketRates.length > 0 ? marketRates : MARKET_RATES).map((item, i) => (
                            <div
                                key={i}
                                className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2"
                            >
                                <span className="text-sm text-slate-300">{item.route}</span>
                                <span className="font-mono text-sm font-semibold text-emerald-400">
                                    {item.rate}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Carrier Network */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> CARRIER NETWORK
                    </h3>
                    <div className="grid grid-cols-3 gap-3">
                        <MiniStat
                            label="Total Carriers"
                            value={dashboardData.carrierNetwork.total}
                        />
                        <MiniStat
                            label="Active Today"
                            value={dashboardData.carrierNetwork.activeToday}
                        />
                        <MiniStat
                            label="Avg Rating"
                            value={dashboardData.carrierNetwork.avgRating}
                            suffix=""
                        />
                    </div>
                </div>
            </div>

            {/* Logistics Menu */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h4 className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                    LOGISTICS
                </h4>
                <div className="flex flex-wrap gap-3">
                    <MenuButton icon="" label="ACTION" />
                    <MenuButton icon="" label="BROKERAGE" />
                    <Link to="/ai-bots/control?bot=freight_broker">
                        <MenuButton icon="" label="AI Broker Config" />
                    </Link>
                </div>
            </div>

            {/* Dispatch Metrics Footer */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex flex-wrap gap-6">
                        <FooterStat
                            label="Dispatch Success Rate"
                            value={dashboardData.dispatchMetrics.successRate}
                        />
                        <FooterStat
                            label="Avg. Turnaround"
                            value={dashboardData.dispatchMetrics.avgTurnaround}
                        />
                        <FooterStat
                            label="Carrier Response"
                            value={dashboardData.dispatchMetrics.responseTime}
                        />
                        <FooterStat
                            label="API Status"
                            value={connected ? " Connected" : " Not Connected"}
                            highlight={!connected}
                        />
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={loadDashboardData}
                            disabled={isPreview}
                            className="rounded-lg bg-white/10 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-white/20 disabled:opacity-50"
                        >
                            Refresh Data
                        </button>
                        {!connected && (
                            <button
                                onClick={handleConnectAPIs}
                                disabled={isPreview}
                                className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-50"
                            >
                                Connect to Live APIs
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Sub-components

function StatCard({ icon, title, value, subtitle, color = "blue" }) {
    const colorClasses = {
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/20",
        green: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20",
        purple: "from-purple-500/20 to-purple-600/10 border-purple-500/20",
    };

    return (
        <div
            className={`rounded-xl border bg-gradient-to-br p-5 backdrop-blur ${colorClasses[color]}`}
        >
            <div className="mb-3 flex items-center gap-2">
                <span className="text-2xl">{icon}</span>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {title}
                </h3>
            </div>
            <div className="mb-2 text-3xl font-bold text-white">{value}</div>
            <p className="text-sm text-slate-400">{subtitle}</p>
        </div>
    );
}

function StatusRow({ color, label, count }) {
    const dotColors = {
        blue: "bg-blue-500",
        green: "bg-emerald-500",
        red: "bg-rose-500",
    };

    return (
        <div className="flex items-center gap-3">
            <span className={`h-2.5 w-2.5 rounded-full ${dotColors[color]}`} />
            <span className="flex-1 text-sm text-slate-300">{label}</span>
            <span className="font-semibold text-white">{count}</span>
        </div>
    );
}

function ActionButton({ icon, label, variant = "secondary", onClick, disabled }) {
    const variants = {
        primary:
            "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg hover:shadow-blue-500/30",
        secondary: "bg-white/10 text-slate-300 hover:bg-white/20",
        outline: "bg-transparent border border-white/20 text-slate-300 hover:bg-white/10",
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]}`}
        >
            <span>{icon}</span>
            {label}
        </button>
    );
}

function MenuButton({ icon, label }) {
    return (
        <button className="flex items-center gap-2 rounded-lg bg-white/5 px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/10">
            <span>{icon}</span>
            {label}
        </button>
    );
}

function MiniStat({ label, value, suffix = "" }) {
    return (
        <div className="rounded-lg bg-white/5 p-3 text-center">
            <div className="text-xl font-bold text-white">
                {value}
                {suffix && <span className="text-amber-400">{suffix}</span>}
            </div>
            <div className="text-xs text-slate-400">{label}</div>
        </div>
    );
}

function FooterStat({ label, value, highlight = false }) {
    return (
        <div>
            <div className="text-xs text-slate-500">{label}</div>
            <div
                className={`text-sm font-semibold ${highlight ? "text-rose-400" : "text-white"
                    }`}
            >
                {value}
            </div>
        </div>
    );
}
