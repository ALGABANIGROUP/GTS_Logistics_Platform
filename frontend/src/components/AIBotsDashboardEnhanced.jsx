/**
 * AI Bots Dashboard (Enhanced)
 * Comprehensive dashboard for all AI bots with BOS integration
 */
import React, { useEffect, useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import axiosClient from "../api/axiosClient";
import SystemReadinessGate from "./SystemReadinessGate.jsx";

const APPROVED_BOT_CATALOG = {
    customer_service: {
        name: "AI Customer Service",
        route: "/ai-bots/customer-service",
        layer: "operations",
        color: "from-sky-500 to-cyan-500",
        description: "Customer support, intake, and service coordination."
    },
    documents_manager: {
        name: "AI Documents Manager",
        route: "/ai-bots/documents",
        layer: "operations",
        color: "from-amber-500 to-orange-500",
        description: "Document processing, compliance, and archive control."
    },
    general_manager: {
        name: "AI General Manager",
        route: "/ai-bots/general-manager",
        layer: "executive",
        color: "from-indigo-600 to-purple-600",
        description: "Executive oversight and strategic reporting."
    },
    information_coordinator: {
        name: "AI Information Coordinator",
        route: "/ai-bots/information",
        layer: "coordination",
        color: "from-violet-500 to-indigo-500",
        description: "Knowledge routing and intelligence coordination."
    },
    intelligence_bot: {
        name: "AI Intelligence Bot",
        route: "/ai-bots/control?bot=intelligence_bot",
        layer: "executive",
        color: "from-indigo-500 to-purple-500",
        description: "Strategic analysis and executive insights."
    },
    legal_bot: {
        name: "AI Legal Consultant",
        route: "/ai-bots/legal",
        layer: "governance",
        color: "from-slate-600 to-gray-600",
        description: "Legal review and compliance guidance."
    },
    maintenance_dev: {
        name: "AI Maintenance Dev",
        route: "/ai-bots/maintenance-dashboard",
        layer: "infrastructure",
        color: "from-slate-600 to-zinc-600",
        description: "System maintenance and health checks."
    },
    mapleload_bot: {
        name: "AI MapleLoad Canada",
        route: "/ai-bots/mapleload-canada",
        layer: "operations",
        color: "from-rose-600 to-red-600",
        description: "Canadian market intelligence and load matching."
    },
    operations_manager_bot: {
        name: "AI Operations Manager",
        route: "/ai-bots/operations",
        layer: "operations",
        color: "from-blue-500 to-indigo-500",
        description: "Operational workflow coordination."
    },
    safety_manager_bot: {
        name: "AI Safety Manager",
        route: "/ai-bots/safety_manager",
        layer: "governance",
        color: "from-amber-600 to-yellow-600",
        description: "Safety compliance and incident tracking."
    },
    sales_bot: {
        name: "AI Sales Bot",
        route: "/ai-bots/sales",
        layer: "operations",
        color: "from-teal-500 to-emerald-500",
        description: "Sales analytics and pipeline support."
    },
    security_manager_bot: {
        name: "AI Security Manager",
        route: "/ai-bots/security_manager",
        layer: "governance",
        color: "from-rose-600 to-red-600",
        description: "Security monitoring and threat response."
    },
    system_manager_bot: {
        name: "AI System Manager",
        route: "/ai-bots/system-admin",
        layer: "infrastructure",
        color: "from-slate-500 to-gray-600",
        description: "System health monitoring and optimization."
    },
    ai_dispatcher: {
        name: "AI Dispatcher",
        route: "/ai-bots/aid-dispatcher",
        layer: "coordination",
        color: "from-sky-600 to-blue-600",
        description: "Intelligent task distribution and routing."
    },
    trainer_bot: {
        name: "AI Trainer Bot",
        route: "/ai-bots/control",
        layer: "governance",
        color: "from-emerald-600 to-teal-600",
        description: "Training and simulation orchestration for bot readiness."
    }
};

const BOT_ALIASES = {
    general_manager: "general_manager",
    information_coordinator: "information_coordinator",
    intelligence_bot: "intelligence_bot",
    executive_intelligence: "intelligence_bot",
    legal_bot: "legal_bot",
    legal_consultant: "legal_bot",
    legal_counsel: "legal_bot",
    maintenance_dev: "maintenance_dev",
    dev_maintenance: "maintenance_dev",
    documents_manager: "documents_manager",
    customer_service: "customer_service",
    operations_manager: "operations_manager_bot",
    operations_bot: "operations_manager_bot",
    operations_manager_bot: "operations_manager_bot",
    safety_manager: "safety_manager_bot",
    safety_bot: "safety_manager_bot",
    safety_manager_bot: "safety_manager_bot",
    security_manager: "security_manager_bot",
    security_bot: "security_manager_bot",
    security_manager_bot: "security_manager_bot",
    system_admin: "system_manager_bot",
    system_manager: "system_manager_bot",
    system_bot: "system_manager_bot",
    system_manager_bot: "system_manager_bot",
    mapleload: "mapleload_bot",
    mapleload_canada: "mapleload_bot",
    mapleload_bot: "mapleload_bot",
    sales: "sales_bot",
    sales_team: "sales_bot",
    sales_bot: "sales_bot",
    ai_dispatcher: "ai_dispatcher",
    aid_dispatcher: "ai_dispatcher",
    dispatcher: "ai_dispatcher",
    trainer_bot: "trainer_bot",
    trainer: "trainer_bot",
    training_bot: "trainer_bot"
};

const normalizeBotKey = (value) => {
    const raw = String(value || "").trim();
    if (!raw) return "";
    return raw.toLowerCase().replace(/[^a-z0-9_]/g, "_");
};

const resolveBotKey = (value) => {
    const normalized = normalizeBotKey(value);
    if (!normalized) return "";
    const canonical = BOT_ALIASES[normalized] || normalized;
    return APPROVED_BOT_CATALOG[canonical] ? canonical : "";
};

const LAYER_CONFIG = {
    executive: { name: "Executive", icon: "EX", order: 1 },
    coordination: { name: "Coordination", icon: "CO", order: 2 },
    operations: { name: "Operations", icon: "OP", order: 3 },
    governance: { name: "Governance", icon: "GV", order: 4 },
    infrastructure: { name: "Infrastructure", icon: "INF", order: 5 },
};

const buildIcon = (botKey) => {
    if (!botKey) return "AI";
    const parts = botKey.split("_").filter(Boolean);
    const initials = parts.map((part) => part[0]?.toUpperCase() || "").join("");
    return initials.slice(0, 3) || "AI";
};

export default function AIBotsDashboardEnhanced() {
    const [bots, setBots] = useState([]);
    const [bosStats, setBosStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState("grid"); // grid | layer
    const [filter, setFilter] = useState("all");
    const navigate = useNavigate();

    const loadBots = useCallback(async () => {
        try {
            setLoading(true);
            const [botsRes, bosRes] = await Promise.all([
                axiosClient.get("/api/v1/ai/bots/available").catch(() => ({ data: { bots: [] } })),
                axiosClient.get("/api/v1/bots").catch(() => ({ data: { bots: [] } })),
            ]);

            const botsPayload = botsRes?.data?.data ?? botsRes?.data ?? {};
            const list = botsPayload?.bots ?? [];
            const bosBots = bosRes?.data?.bots || [];

            const mapped = list.reduce((acc, bot) => {
                const rawKey = bot.bot_key || bot.bot_code || bot.botKey || bot.name;
                const botKey = resolveBotKey(rawKey);
                if (!botKey || acc.has(botKey)) return acc;

                const config = APPROVED_BOT_CATALOG[botKey];
                const bosBot = bosBots.find((b) => resolveBotKey(b.name) === botKey);
                const title = config.name || bot.display_name || bot.name || botKey;
                const desc = config.description || bot.description || "AI assistant";
                const hasBackend = bot.has_backend !== false;

                const basePath = config.route || "/ai-bots/control";
                const path = hasBackend
                    ? basePath === "/ai-bots/control" && botKey
                        ? `${basePath}?bot=${encodeURIComponent(botKey)}`
                        : basePath
                    : `/ai-bots/control?mode=preview&bot=${encodeURIComponent(botKey)}`;

                acc.set(botKey, {
                    botKey,
                    icon: buildIcon(botKey),
                    title,
                    desc,
                    path,
                    hasBackend,
                    layer: config.layer,
                    color: config.color,
                    // BOS data
                    enabled: bosBot?.enabled !== false,
                    lastRun: bosBot?.last_run,
                    nextRun: bosBot?.next_run,
                    schedule: bosBot?.schedule,
                    automation: bosBot?.automation_level,
                });

                return acc;
            }, new Map());

            setBots(Array.from(mapped.values()));

            // Calculate stats
            const approvedBots = Array.from(mapped.values());
            setBosStats({
                total: approvedBots.length,
                active: approvedBots.filter(b => b.hasBackend && b.enabled).length,
                preview: approvedBots.filter(b => !b.hasBackend).length,
                paused: approvedBots.filter(b => b.hasBackend && !b.enabled).length,
            });
        } catch (err) {
            console.error("Failed to load bots:", err);
            setBots([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadBots();
    }, [loadBots]);

    // Filter bots
    const filteredBots = bots.filter(bot => {
        if (filter === "all") return true;
        if (filter === "active") return bot.hasBackend && bot.enabled;
        if (filter === "preview") return !bot.hasBackend;
        if (filter === "paused") return bot.hasBackend && !bot.enabled;
        return true;
    });

    // Group by layer for layer view
    const botsByLayer = filteredBots.reduce((acc, bot) => {
        const layer = bot.layer || "operations";
        if (!acc[layer]) acc[layer] = [];
        acc[layer].push(bot);
        return acc;
    }, {});

    return (
        <SystemReadinessGate>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-white">AI Bots Dashboard</h1>
                        <p className="mt-1 text-sm text-slate-300">
                            Manage and monitor your AI bot network
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            to="/ai-bots/bot-os"
                            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg hover:shadow-blue-500/30"
                        >
                            <span className="text-xs">BOS</span>
                            BOS Control Center
                        </Link>
                    </div>
                </div>

                {/* Stats Row */}
                {bosStats && (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                        <StatCard
                            label="Total Bots"
                            value={bosStats.total}
                            icon="ALL"
                            color="blue"
                        />
                        <StatCard
                            label="Active"
                            value={bosStats.active}
                            icon="ACT"
                            color="green"
                        />
                        <StatCard
                            label="Preview Mode"
                            value={bosStats.preview}
                            icon="PRE"
                            color="amber"
                        />
                        <StatCard
                            label="Paused"
                            value={bosStats.paused}
                            icon="PAU"
                            color="slate"
                        />
                    </div>
                )}

                {/* Controls */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                    {/* Filter */}
                    <div className="flex items-center gap-2">
                        {[
                            { id: "all", label: "All Bots" },
                            { id: "active", label: "Active" },
                            { id: "preview", label: "Preview" },
                        ].map((f) => (
                            <button
                                key={f.id}
                                onClick={() => setFilter(f.id)}
                                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${filter === f.id
                                        ? "bg-white/15 text-white ring-1 ring-white/20"
                                        : "bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                {f.label}
                            </button>
                        ))}
                    </div>

                    {/* View Toggle */}
                    <div className="flex items-center gap-1 rounded-lg bg-white/5 p-1">
                        <button
                            onClick={() => setViewMode("grid")}
                            className={`rounded px-3 py-1 text-xs font-medium transition ${viewMode === "grid"
                                    ? "bg-white/15 text-white"
                                    : "text-slate-400 hover:text-white"
                                }`}
                        >
                            Grid
                        </button>
                        <button
                            onClick={() => setViewMode("layer")}
                            className={`rounded px-3 py-1 text-xs font-medium transition ${viewMode === "layer"
                                    ? "bg-white/15 text-white"
                                    : "text-slate-400 hover:text-white"
                                }`}
                        >
                            By Layer
                        </button>
                    </div>
                </div>

                {/* Content */}
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="text-sm text-slate-400">Loading bots...</div>
                    </div>
                ) : filteredBots.length === 0 ? (
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-12 text-center">
                        <div className="text-3xl">AI</div>
                        <p className="mt-2 text-sm text-slate-400">No bots found</p>
                    </div>
                ) : viewMode === "grid" ? (
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {filteredBots.map((bot) => (
                            <BotCard key={bot.botKey} bot={bot} />
                        ))}
                    </div>
                ) : (
                    <div className="space-y-6">
                        {Object.entries(LAYER_CONFIG)
                            .sort((a, b) => a[1].order - b[1].order)
                            .map(([layerId, layerConfig]) => {
                                const layerBots = botsByLayer[layerId];
                                if (!layerBots?.length) return null;

                                return (
                                    <div key={layerId}>
                                        <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                                            <span>{layerConfig.icon}</span>
                                            {layerConfig.name} Layer
                                            <span className="text-xs text-slate-500">({layerBots.length})</span>
                                        </h3>
                                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                            {layerBots.map((bot) => (
                                                <BotCard key={bot.botKey} bot={bot} />
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                )}
            </div>
        </SystemReadinessGate>
    );
}

function BotCard({ bot }) {
    return (
        <Link
            to={bot.path}
            className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur transition hover:bg-white/10 hover:border-white/20"
        >
            {/* Background Gradient */}
            <div
                className={`absolute inset-0 bg-gradient-to-br ${bot.color} opacity-5 transition group-hover:opacity-10`}
            />

            <div className="relative flex items-start gap-4">
                {/* Icon */}
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${bot.color} text-2xl shadow-lg`}>
                    {bot.icon}
                </div>

                {/* Content */}
                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                        <h3 className="truncate text-base font-semibold text-white group-hover:text-blue-200">
                            {bot.title}
                        </h3>
                        {!bot.hasBackend && (
                            <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-semibold text-amber-300">
                                Preview
                            </span>
                        )}
                        {bot.hasBackend && !bot.enabled && (
                            <span className="rounded-full bg-slate-500/20 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
                                Paused
                            </span>
                        )}
                    </div>
                    <p className="mt-1 line-clamp-2 text-sm text-slate-400">
                        {bot.desc}
                    </p>

                    {/* Schedule Info */}
                    {bot.hasBackend && bot.schedule && (
                        <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
                            <span>Schedule:</span>
                            <span className="font-mono">{bot.schedule}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Status Indicator */}
            <div className={`absolute right-3 top-3 h-2 w-2 rounded-full ${!bot.hasBackend
                    ? "bg-amber-500"
                    : bot.enabled
                        ? "bg-emerald-500"
                        : "bg-slate-500"
                }`} />
        </Link>
    );
}

function StatCard({ label, value, icon, color }) {
    const colorClasses = {
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/20",
        green: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20",
        amber: "from-amber-500/20 to-amber-600/10 border-amber-500/20",
        slate: "from-slate-500/20 to-slate-600/10 border-slate-500/20",
    };

    return (
        <div className={`rounded-xl border bg-gradient-to-br p-4 ${colorClasses[color]}`}>
            <div className="flex items-center gap-2 text-slate-400">
                <span className="text-lg">{icon}</span>
                <span className="text-xs font-medium">{label}</span>
            </div>
            <div className="mt-1 text-2xl font-bold text-white">{value}</div>
        </div>
    );
}
