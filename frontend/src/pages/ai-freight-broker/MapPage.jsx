import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Settings, Eye, Truck, Package, Clock, Route } from 'lucide-react';
import GlassCard from '../../components/ui/GlassCard';
import fleetSafetyApi from '../../services/fleetSafetyApi';

const MapPage = () => {
    const navigate = useNavigate();
    const [fleetStats, setFleetStats] = useState(null);

    useEffect(() => {
        fleetSafetyApi.getLiveMapData()
            .then((response) => setFleetStats(response.data?.stats || null))
            .catch(() => setFleetStats(null));
    }, []);

    const handleConfigureMap = () => {
        navigate('/admin/settings?tab=integrations&section=maps');
    };

    const handleGoToShipments = () => {
        navigate('/ai-bots/freight_broker/shipments');
    };

    const handleOpenFleetMap = () => {
        navigate('/ai-bots/freight_broker/live-map');
    };

    return (
        <div className="ai-freight-page space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="text-2xl font-semibold text-white">Live Freight Map</div>
                    <div className="text-sm text-slate-300">
                        Track shipments and trucks in real-time
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        className="rounded-lg border border-emerald-400/20 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-100 hover:bg-emerald-500/20"
                        onClick={handleOpenFleetMap}
                    >
                        <Route size={14} />
                        Fleet Live Map
                    </button>
                    <button
                        className="rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/10 hover:text-white"
                        onClick={handleGoToShipments}
                    >
                        <Eye size={14} />
                        View Shipments
                    </button>
                </div>
            </div>

            <GlassCard className="p-6 bg-white/5 border border-white/10 backdrop-blur">
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <div className="mb-6">
                        <MapPin size={64} className="text-slate-300 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">Interactive Freight Map</h3>
                        <p className="text-slate-300 max-w-md">
                            Shipment mapping stays separate for now, but the new fleet live layer is online and connected to fleet drivers, vehicles, tracks, and alerts.
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            className="rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-white/10 hover:text-white"
                            onClick={handleConfigureMap}
                        >
                            <Settings size={16} className="inline mr-2" />
                            Configure Map
                        </button>
                        <button
                            className="rounded-lg border border-emerald-400/20 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-100 hover:bg-emerald-500/20"
                            onClick={handleOpenFleetMap}
                        >
                            <Truck size={16} className="inline mr-2" />
                            Open Fleet Live Map
                        </button>
                        <button
                            className="rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-white/10 hover:text-white"
                            onClick={handleGoToShipments}
                        >
                            <Package size={16} className="inline mr-2" />
                            Go to Shipments
                        </button>
                    </div>
                </div>
            </GlassCard>

            {/* Quick stats */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <GlassCard className="p-4 bg-white/5 border border-white/10 backdrop-blur">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20">
                            <Truck size={20} className="text-emerald-300" />
                        </div>
                        <div>
                            <div className="text-lg font-bold text-white">{fleetStats?.active_vehicles ?? 42}</div>
                            <div className="text-xs text-slate-300">Fleet Vehicles Online</div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-4 bg-white/5 border border-white/10 backdrop-blur">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/20">
                            <Package size={20} className="text-sky-300" />
                        </div>
                        <div>
                            <div className="text-lg font-bold text-white">18</div>
                            <div className="text-xs text-slate-300">Shipments in Transit</div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-4 bg-white/5 border border-white/10 backdrop-blur">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/20">
                            <Clock size={20} className="text-amber-300" />
                        </div>
                        <div>
                            <div className="text-lg font-bold text-white">{fleetStats?.alerts_open ?? 0}</div>
                            <div className="text-xs text-slate-300">Fleet Alerts Open</div>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* Map Legend */}
            <GlassCard className="p-4 bg-white/5 border border-white/10 backdrop-blur">
                <div className="text-sm font-semibold text-white mb-4">Map Legend</div>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full bg-emerald-500"></div>
                        <span className="text-sm text-slate-300">Active Truck</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full bg-sky-500"></div>
                        <span className="text-sm text-slate-300">In Transit</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full bg-amber-500"></div>
                        <span className="text-sm text-slate-300">Pending Pickup</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full bg-rose-500"></div>
                        <span className="text-sm text-slate-300">Delayed</span>
                    </div>
                </div>
            </GlassCard>
        </div>
    );
};

export default MapPage;
