import React, { useEffect, useMemo, useState } from "react";
import { RefreshCw, Search, Truck, MapPin, DollarSign, Package } from "lucide-react";
import axiosClient from "../../api/axiosClient";
import GlassCard from "../../components/ui/GlassCard";

const initialFilters = {
    origin: "",
    destination: "",
    trailer: "",
};

const formatMoney = (value) =>
    new Intl.NumberFormat("en-CA", {
        style: "currency",
        currency: "CAD",
        maximumFractionDigits: 0,
    }).format(Number(value || 0));

const normalizeLoad = (load) => ({
    id: load.load_id || load.id,
    origin: [load.origin_city, load.origin_province].filter(Boolean).join(", ") || load.origin || "-",
    destination:
        [load.destination_city, load.destination_province || load.destination_country]
            .filter(Boolean)
            .join(", ") || load.destination || "-",
    trailer: load.trailer_type || load.trailer || "Any",
    weight: load.weight_lbs || load.weight || 0,
    rate: load.rate_cad || load.rate || 0,
    postedAge: load.posted_age || load.age || "-",
});

const AIFreightBrokerDashboard = () => {
    const [filters, setFilters] = useState(initialFilters);
    const [draftFilters, setDraftFilters] = useState(initialFilters);
    const [loads, setLoads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");

    const fetchLoads = async (nextFilters = filters, background = false) => {
        if (background) setRefreshing(true);
        else setLoading(true);
        setError("");
        try {
            const response = await axiosClient.get("/api/v1/freight/canadian-loads", {
                params: {
                    origin: nextFilters.origin || undefined,
                    destination: nextFilters.destination || undefined,
                    trailer: nextFilters.trailer || undefined,
                },
            });
            const items = Array.isArray(response?.data?.loads) ? response.data.loads.map(normalizeLoad) : [];
            setLoads(items);
        } catch (err) {
            setLoads([]);
            setError(err?.response?.data?.detail || err?.message || "Failed to load freight marketplace data.");
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchLoads(filters);
    }, []);

    const kpis = useMemo(() => {
        const total = loads.length;
        const totalValue = loads.reduce((sum, load) => sum + Number(load.rate || 0), 0);
        const avgRate = total ? totalValue / total : 0;
        const avgWeight = total
            ? Math.round(loads.reduce((sum, load) => sum + Number(load.weight || 0), 0) / total)
            : 0;

        return [
            { label: "Available Loads", value: total, icon: <Package size={18} className="text-sky-300" /> },
            { label: "Average Rate", value: formatMoney(avgRate), icon: <DollarSign size={18} className="text-emerald-300" /> },
            { label: "Average Weight", value: avgWeight ? `${avgWeight.toLocaleString()} lbs` : "-", icon: <Truck size={18} className="text-amber-300" /> },
            {
                label: "Active Corridors",
                value: new Set(loads.map((load) => `${load.origin}-${load.destination}`)).size,
                icon: <MapPin size={18} className="text-rose-300" />,
            },
        ];
    }, [loads]);

    const handleSearch = () => {
        setFilters(draftFilters);
        fetchLoads(draftFilters);
    };

    return (
        <div className="ai-freight-page space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="text-2xl font-semibold text-white">AI Freight Broker Dashboard</div>
                    <div className="text-sm text-slate-300">Live Canadian freight marketplace view</div>
                </div>
                <button
                    className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15"
                    onClick={() => fetchLoads(filters, true)}
                    disabled={refreshing}
                >
                    <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
                    {refreshing ? "Refreshing..." : "Refresh"}
                </button>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                {kpis.map((item) => (
                    <GlassCard key={item.label} className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-xs text-slate-400">{item.label}</div>
                                <div className="mt-2 text-2xl font-bold text-white">{item.value}</div>
                            </div>
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                                {item.icon}
                            </div>
                        </div>
                    </GlassCard>
                ))}
            </div>

            <GlassCard className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                <div className="mb-4 flex items-center gap-2 text-white">
                    <Search size={16} />
                    <span className="font-semibold">Load Search</span>
                </div>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                    <input
                        value={draftFilters.origin}
                        onChange={(e) => setDraftFilters((prev) => ({ ...prev, origin: e.target.value }))}
                        placeholder="Origin"
                        className="rounded-lg border border-white/15 bg-slate-950/50 px-3 py-2 text-sm text-white placeholder:text-slate-500"
                    />
                    <input
                        value={draftFilters.destination}
                        onChange={(e) => setDraftFilters((prev) => ({ ...prev, destination: e.target.value }))}
                        placeholder="Destination"
                        className="rounded-lg border border-white/15 bg-slate-950/50 px-3 py-2 text-sm text-white placeholder:text-slate-500"
                    />
                    <input
                        value={draftFilters.trailer}
                        onChange={(e) => setDraftFilters((prev) => ({ ...prev, trailer: e.target.value }))}
                        placeholder="Trailer Type"
                        className="rounded-lg border border-white/15 bg-slate-950/50 px-3 py-2 text-sm text-white placeholder:text-slate-500"
                    />
                    <button
                        onClick={handleSearch}
                        className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                    >
                        Search Loads
                    </button>
                </div>
            </GlassCard>

            <GlassCard className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                <div className="mb-4 text-lg font-semibold text-white">Available Loads</div>
                {error ? <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">{error}</div> : null}
                {loading ? (
                    <div className="py-10 text-center text-slate-300">Loading freight data...</div>
                ) : loads.length === 0 ? (
                    <div className="py-10 text-center text-slate-400">No live loads matched the current filters.</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full min-w-[720px]">
                            <thead>
                                <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-slate-400">
                                    <th className="px-3 py-3">Origin</th>
                                    <th className="px-3 py-3">Destination</th>
                                    <th className="px-3 py-3">Trailer</th>
                                    <th className="px-3 py-3">Weight</th>
                                    <th className="px-3 py-3">Rate</th>
                                    <th className="px-3 py-3">Posted</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loads.map((load) => (
                                    <tr key={load.id} className="border-b border-white/5 text-sm text-slate-200">
                                        <td className="px-3 py-3">{load.origin}</td>
                                        <td className="px-3 py-3">{load.destination}</td>
                                        <td className="px-3 py-3">{load.trailer}</td>
                                        <td className="px-3 py-3">{Number(load.weight || 0).toLocaleString()}</td>
                                        <td className="px-3 py-3 text-emerald-300">{formatMoney(load.rate)}</td>
                                        <td className="px-3 py-3 text-slate-400">{load.postedAge}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </GlassCard>
        </div>
    );
};

export default AIFreightBrokerDashboard;
