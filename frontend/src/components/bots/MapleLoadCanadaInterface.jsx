/**
 * MapleLoad Canada Bot Interface
 * Specialized interface for the MDP (MapleLoad Canada) bot
 * Canadian market intelligence, carrier discovery, and cross-border operations
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../api/axiosClient";
import BotControlInterface from "./BotControlInterface";

const BOT_KEY = "mapleload_canada";

const QUICK_ACTIONS = [
    { id: "market_intel", label: "Canada Market Intel", icon: "", command: "get_canada_market_intelligence" },
    { id: "carriers", label: "Find Carriers", icon: "", command: "discover_canadian_carriers" },
    { id: "crossborder", label: "Cross-Border Analysis", icon: "", command: "analyze_cross_border_routes" },
    { id: "compliance", label: "Compliance Check", icon: "", command: "check_compliance" },
    { id: "rates", label: "Rate Comparison", icon: "", command: "compare_canadian_rates" },
];

const PROVINCES = [
    "Ontario", "Quebec", "British Columbia", "Alberta",
    "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick",
    "Newfoundland", "Prince Edward Island"
];

export default function MapleLoadCanadaInterface({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeSection, setActiveSection] = useState("overview");
    const [marketData, setMarketData] = useState(null);
    const [carriers, setCarriers] = useState([]);
    const [crossBorderRoutes, setCrossBorderRoutes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Bot configuration
    const botConfig = {
        displayName: "MapleLoad Canada",
        type: "Market Intelligence",
        mode: isPreview ? "preview" : "active",
        capabilities: [
            "Canadian Market Intelligence",
            "Carrier Discovery & Verification",
            "Cross-Border Route Optimization",
            "Compliance & Regulatory Checks",
            "Rate Benchmarking",
            "Provincial Analysis",
        ],
        commands: QUICK_ACTIONS,
    };

    // Load market overview
    const loadMarketData = useCallback(async () => {
        if (isPreview) return;
        setLoading(true);
        try {
            const res = await axiosClient.post(
                `/api/v1/ai/bots/available/${BOT_KEY}/run`,
                { message: "get_canada_market_intelligence", context: { summary: true } }
            );
            setMarketData(res?.data?.result || res?.data || null);
        } catch (err) {
            console.warn("Market data load failed:", err);
        } finally {
            setLoading(false);
        }
    }, [isPreview]);

    useEffect(() => {
        loadMarketData();
    }, [loadMarketData]);

    return (
        <div className="space-y-6">
            {/* Canada-specific Header */}
            <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 p-6 backdrop-blur-xl shadow-2xl">
                <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-red-500 to-red-700 text-3xl shadow-lg">
                        <img
                            src="/canada-maple-leaf.svg"
                            alt="Canada Maple Leaf"
                            style={{ width: '40px', height: '40px' }}
                        />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">MapleLoad Canada</h1>
                        <p className="text-sm text-slate-400">
                            Canadian Market Intelligence & Cross-Border Operations
                        </p>
                    </div>
                    <div className="ml-auto flex items-center gap-2">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${isPreview
                            ? "bg-amber-500/20 text-amber-300"
                            : "bg-emerald-500/20 text-emerald-300"
                            }`}>
                            {isPreview ? "Preview Mode" : "Active"}
                        </span>
                    </div>
                </div>

                {/* Quick Stats Row */}
                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <QuickStat label="Active Carriers" value={carriers.length || ""} icon="" />
                    <QuickStat label="Provinces" value="10" icon="" />
                    <QuickStat label="Cross-Border Routes" value={crossBorderRoutes.length || ""} icon="" />
                    <QuickStat
                        label="Market Status"
                        value={marketData?.status || "Loading..."}
                        icon=""
                    />
                </div>
            </div>

            {/* Quick Actions */}
            <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 p-5 backdrop-blur-xl shadow-2xl">
                <h3 className="mb-4 text-sm font-semibold text-white"> Quick Actions</h3>
                <div className="flex flex-wrap gap-2">
                    {QUICK_ACTIONS.map((action) => (
                        <button
                            key={action.id}
                            disabled={isPreview}
                            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${isPreview
                                ? "bg-slate-700/50 text-slate-500 cursor-not-allowed"
                                : "bg-gradient-to-r from-red-600/80 to-red-700/80 text-white shadow hover:from-red-500/80 hover:to-red-600/80"
                                }`}
                        >
                            <span>{action.icon}</span>
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Provincial Coverage Map (Simplified) */}
            <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 p-5 backdrop-blur-xl shadow-2xl">
                <h3 className="mb-4 text-sm font-semibold text-white"> Provincial Coverage</h3>
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
                    {PROVINCES.map((province) => (
                        <div
                            key={province}
                            className="flex items-center gap-2 rounded-lg border border-slate-700/30 bg-slate-800/40 p-3 backdrop-blur"
                        >
                            <span className="text-emerald-400"></span>
                            <span className="text-xs text-slate-300">{province}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Bot Interface */}
            <BotControlInterface
                botKey={BOT_KEY}
                botConfig={botConfig}
                mode={mode}
            />

            {/* Cross-Border Section */}
            <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 p-5 backdrop-blur-xl shadow-2xl">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                    <span></span> Cross-Border Intelligence
                </h3>
                <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-xl border border-slate-700/30 bg-slate-800/40 p-4 backdrop-blur">
                        <h4 className="mb-3 text-xs font-semibold text-slate-400">
                            Key Border Crossings
                        </h4>
                        <div className="space-y-2">
                            {[
                                { name: "Windsor-Detroit", status: "Open", volume: "High" },
                                { name: "Niagara Falls", status: "Open", volume: "Medium" },
                                { name: "Pacific Highway", status: "Open", volume: "High" },
                                { name: "Lacolle-Champlain", status: "Open", volume: "Medium" },
                            ].map((crossing) => (
                                <div
                                    key={crossing.name}
                                    className="flex items-center justify-between rounded-lg border border-slate-700/30 bg-slate-900/60 px-3 py-2 backdrop-blur"
                                >
                                    <span className="text-xs text-white">{crossing.name}</span>
                                    <div className="flex items-center gap-2">
                                        <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-300">
                                            {crossing.status}
                                        </span>
                                        <span className="text-xs text-slate-400">{crossing.volume}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="rounded-xl border border-slate-700/30 bg-slate-800/40 p-4 backdrop-blur">
                        <h4 className="mb-3 text-xs font-semibold text-slate-400">
                            Compliance Requirements
                        </h4>
                        <div className="space-y-2 text-xs text-slate-300">
                            <div className="flex items-center gap-2">
                                <span className="text-emerald-400"></span>
                                CBSA Registration
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-emerald-400"></span>
                                C-TPAT / PIP Certification
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-emerald-400"></span>
                                FAST Card Eligibility
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-emerald-400"></span>
                                eManifest Compliance
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function QuickStat({ label, value, icon }) {
    return (
        <div className="rounded-xl border border-slate-700/30 bg-slate-800/40 p-3 backdrop-blur">
            <div className="flex items-center gap-2 text-slate-400">
                <span className="text-base">{icon}</span>
                <span className="text-xs font-medium">{label}</span>
            </div>
            <div className="mt-1 truncate text-sm font-semibold text-white">{value}</div>
        </div>
    );
}
