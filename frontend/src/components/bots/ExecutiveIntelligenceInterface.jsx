/**
 * Executive Intelligence (GIT) Bot Interface
 * General Intelligence & Tracking - Executive oversight and strategic analysis
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../api/axiosClient";
import BotControlInterface from "./BotControlInterface";

const BOT_KEY = "executive_intelligence";

const QUICK_ACTIONS = [
    { id: "kpis", label: "Executive KPIs", icon: "", command: "get_executive_kpis" },
    { id: "strategic", label: "Strategic Analysis", icon: "", command: "strategic_analysis" },
    { id: "market", label: "Market Intelligence", icon: "", command: "market_intelligence" },
    { id: "trends", label: "Industry Trends", icon: "", command: "industry_trends" },
    { id: "risks", label: "Risk Assessment", icon: "", command: "risk_assessment" },
];

export default function ExecutiveIntelligenceInterface({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [kpiData, setKpiData] = useState(null);
    const [trendData, setTrendData] = useState([]);
    const [loading, setLoading] = useState(false);

    const loadDashboardData = useCallback(async () => {
        setLoading(true);
        try {
            const [metricsRes, trendsRes] = await Promise.all([
                axiosClient.get("/coordinator/dashboard/metrics"),
                axiosClient.get("/coordinator/analytics/trends"),
            ]);
            setKpiData(metricsRes?.data?.metrics || null);
            setTrendData(Array.isArray(trendsRes?.data?.trends) ? trendsRes.data.trends : []);
        } catch (error) {
            setKpiData(null);
            setTrendData([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!isPreview) {
            loadDashboardData();
        }
    }, [isPreview, loadDashboardData]);

    const botConfig = {
        displayName: "Executive Intelligence (GIT)",
        type: "Executive Bot",
        mode: isPreview ? "preview" : "active",
        capabilities: [
            "Executive KPI Monitoring",
            "Strategic Analysis",
            "Market Intelligence",
            "Competitive Analysis",
            "Risk Assessment",
            "Industry Trend Tracking",
        ],
        commands: QUICK_ACTIONS,
    };

    return (
        <div className="space-y-6">
            {/* Executive Header */}
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-indigo-900/30 via-slate-900/90 to-purple-900/30 p-5 backdrop-blur">
                <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-3xl shadow-lg">

                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">Executive Intelligence</h1>
                        <p className="text-sm text-slate-400">
                            General Intelligence & Tracking (GIT) - Strategic Oversight
                        </p>
                    </div>
                    <div className="ml-auto">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${isPreview
                            ? "bg-amber-500/20 text-amber-300"
                            : "bg-emerald-500/20 text-emerald-300"
                            }`}>
                            {isPreview ? "Preview Mode" : "Active"}
                        </span>
                    </div>
                </div>

                {/* Executive Dashboard Stats */}
                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
                    <QuickStat
                        label="Daily Revenue"
                        value={formatCurrency(kpiData?.financial?.daily_revenue)}
                        icon=""
                    />
                    <QuickStat
                        label="Monthly Revenue"
                        value={formatCurrency(kpiData?.financial?.monthly_revenue)}
                        icon=""
                    />
                    <QuickStat
                        label="Completed Today"
                        value={formatCount(kpiData?.shipments?.completed_today)}
                        icon=""
                    />
                    <QuickStat
                        label="Active Shipments"
                        value={formatCount(kpiData?.shipments?.total_active)}
                        icon=""
                    />
                    <QuickStat
                        label="Total Customers"
                        value={formatCount(kpiData?.customers?.total_customers)}
                        icon=""
                    />
                </div>
            </div>

            {/* Strategic Overview */}
            <div className="grid gap-4 lg:grid-cols-3">
                {/* KPI Panel */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
                    <h3 className="mb-3 text-sm font-semibold text-white"> Key Performance Indicators</h3>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <KPICard
                            title="Monthly Revenue"
                            value={formatCurrency(kpiData?.financial?.monthly_revenue)}
                            target="Based on live payments"
                            status="above"
                        />
                        <KPICard
                            title="Daily Revenue"
                            value={formatCurrency(kpiData?.financial?.daily_revenue)}
                            target="Current day"
                            status="above"
                        />
                        <KPICard
                            title="Completed Shipments"
                            value={formatCount(kpiData?.shipments?.completed_today)}
                            target="Current day"
                            status="above"
                        />
                        <KPICard
                            title="Customer Base"
                            value={formatCount(kpiData?.customers?.total_customers)}
                            target="Current total"
                            status="above"
                        />
                    </div>
                </div>

                {/* Risk Assessment */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white"> Risk Assessment</h3>
                    {trendData.length === 0 ? (
                        <div className="text-xs text-slate-400">
                            {loading ? "Loading trend indicators..." : "No trend indicators available."}
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {trendData.map((trend) => (
                                <RiskItem
                                    key={trend.metric}
                                    level={mapTrendLevel(trend.trend)}
                                    text={`${trend.metric}: ${trend.value ?? "n/a"}`}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-3 text-sm font-semibold text-white"> Quick Actions</h3>
                <div className="flex flex-wrap gap-2">
                    {QUICK_ACTIONS.map((action) => (
                        <button
                            key={action.id}
                            disabled={isPreview}
                            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${isPreview
                                ? "bg-slate-700/50 text-slate-500 cursor-not-allowed"
                                : "bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white shadow hover:from-indigo-500/80 hover:to-purple-500/80"
                                }`}
                        >
                            <span>{action.icon}</span>
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Bot Interface */}
            <BotControlInterface
                botKey={BOT_KEY}
                botConfig={botConfig}
                mode={mode}
            />
        </div>
    );
}

function formatCurrency(value) {
    if (typeof value !== "number") {
        return "N/A";
    }
    return `$${value.toLocaleString()}`;
}

function formatCount(value) {
    if (typeof value !== "number") {
        return "N/A";
    }
    return value.toLocaleString();
}

function mapTrendLevel(trend) {
    if (trend === "up") {
        return "low";
    }
    if (trend === "down") {
        return "high";
    }
    return "medium";
}

function QuickStat({ label, value, trend, icon }) {
    return (
        <div className="rounded-xl bg-white/5 p-3">
            <div className="flex items-center justify-between text-slate-400">
                <span className="text-base">{icon}</span>
                {trend && (
                    <span className="text-xs font-medium text-emerald-400">{trend}</span>
                )}
            </div>
            <div className="mt-1 text-sm font-bold text-white">{value}</div>
            <div className="text-xs text-slate-400">{label}</div>
        </div>
    );
}

function KPICard({ title, value, target, status }) {
    const statusColor = status === "above" ? "text-emerald-400" : status === "below" ? "text-emerald-400" : "text-amber-400";

    return (
        <div className="rounded-lg bg-white/5 p-3">
            <div className="text-xs text-slate-400">{title}</div>
            <div className="mt-1 flex items-baseline gap-2">
                <span className={`text-lg font-bold ${statusColor}`}>{value}</span>
                <span className="text-xs text-slate-500">Target: {target}</span>
            </div>
        </div>
    );
}

function RiskItem({ level, text }) {
    const colors = {
        low: "bg-emerald-500/20 text-emerald-300",
        medium: "bg-amber-500/20 text-amber-300",
        high: "bg-rose-500/20 text-rose-300",
    };

    return (
        <div className="flex items-center justify-between rounded-lg bg-white/5 p-2">
            <span className="text-xs text-slate-300">{text}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${colors[level]}`}>
                {level}
            </span>
        </div>
    );
}
