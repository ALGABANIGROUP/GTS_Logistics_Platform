/**
 * Freight Bookings (IT-Freight) Bot Interface
 * Intelligent freight operations, carrier matching, and load booking
 */
import { useState } from "react";
import BotControlInterface from "./BotControlInterface";

const BOT_KEY = "freight_bookings";

const QUICK_ACTIONS = [
    { id: "match", label: "Match Carriers", icon: "", command: "match_carriers" },
    { id: "rates", label: "Get Rates", icon: "", command: "get_rate_quotes" },
    { id: "book", label: "Book Load", icon: "", command: "book_load" },
    { id: "track", label: "Track Shipment", icon: "", command: "track_shipment" },
    { id: "optimize", label: "Route Optimize", icon: "", command: "optimize_routes" },
];

export default function FreightBookingsInterface({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeLoads, setActiveLoads] = useState([
        { id: "LD-2024-001", origin: "Chicago, IL", dest: "Dallas, TX", status: "In Transit", eta: "2h 30m" },
        { id: "LD-2024-002", origin: "Atlanta, GA", dest: "Miami, FL", status: "Pickup", eta: "4h 15m" },
        { id: "LD-2024-003", origin: "Los Angeles, CA", dest: "Phoenix, AZ", status: "Delivered", eta: "" },
    ]);

    const botConfig = {
        displayName: "IT-Freight Bot",
        type: "Freight Operations",
        mode: isPreview ? "preview" : "active",
        capabilities: [
            "Carrier Matching & Selection",
            "Rate Quote Aggregation",
            "Load Booking Automation",
            "Route Optimization",
            "Real-Time Tracking",
            "Delivery Coordination",
        ],
        commands: QUICK_ACTIONS,
    };

    return (
        <div className="space-y-6">
            {/* Freight Header */}
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-blue-900/30 via-slate-900/90 to-cyan-900/30 p-5 backdrop-blur">
                <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 text-3xl shadow-lg">
                        
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">IT-Freight Bot</h1>
                        <p className="text-sm text-slate-400">
                            Intelligent Freight Operations & Carrier Matching
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

                {/* Freight Stats */}
                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
                    <FreightStat label="Active Loads" value="24" icon="" />
                    <FreightStat label="In Transit" value="18" icon="" />
                    <FreightStat label="Pending Pickup" value="6" icon="" />
                    <FreightStat label="Delivered Today" value="12" icon="" />
                    <FreightStat label="On-Time Rate" value="96%" icon="" />
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
                                    : "bg-gradient-to-r from-blue-600/80 to-cyan-600/80 text-white shadow hover:from-blue-500/80 hover:to-cyan-500/80"
                                }`}
                        >
                            <span>{action.icon}</span>
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Active Loads */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-3 text-sm font-semibold text-white"> Active Loads</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-slate-400">
                                <th className="pb-2 pr-4">Load ID</th>
                                <th className="pb-2 pr-4">Origin</th>
                                <th className="pb-2 pr-4">Destination</th>
                                <th className="pb-2 pr-4">Status</th>
                                <th className="pb-2">ETA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {activeLoads.map((load) => (
                                <tr key={load.id} className="border-b border-white/5">
                                    <td className="py-2 pr-4 font-mono text-white">{load.id}</td>
                                    <td className="py-2 pr-4 text-slate-300">{load.origin}</td>
                                    <td className="py-2 pr-4 text-slate-300">{load.dest}</td>
                                    <td className="py-2 pr-4">
                                        <LoadStatus status={load.status} />
                                    </td>
                                    <td className="py-2 text-slate-300">{load.eta}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
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

function FreightStat({ label, value, icon }) {
    return (
        <div className="rounded-xl bg-white/5 p-3">
            <div className="flex items-center gap-2 text-slate-400">
                <span className="text-base">{icon}</span>
                <span className="text-xs font-medium">{label}</span>
            </div>
            <div className="mt-1 text-sm font-bold text-white">{value}</div>
        </div>
    );
}

function LoadStatus({ status }) {
    const statusConfig = {
        "In Transit": { color: "bg-blue-500/20 text-blue-300" },
        "Pickup": { color: "bg-amber-500/20 text-amber-300" },
        "Delivered": { color: "bg-emerald-500/20 text-emerald-300" },
        "Delayed": { color: "bg-rose-500/20 text-rose-300" },
    };

    const config = statusConfig[status] || { color: "bg-slate-500/20 text-slate-300" };

    return (
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${config.color}`}>
            {status}
        </span>
    );
}
