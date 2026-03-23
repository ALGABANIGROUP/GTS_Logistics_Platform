import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
    Package,
    Truck,
    Clock,
    AlertTriangle,
    CheckCircle,
    XCircle,
    MapPin,
    Eye,
    ExternalLink,
    RefreshCw,
    TrendingUp,
    TrendingDown,
    BarChart3,
    Activity
} from 'lucide-react';
import GlassCard from '../../components/ui/GlassCard';
import axiosClient from '../../api/axiosClient';
import { useShipmentWeather } from '../../hooks/useShipmentWeather';
import ShipmentWeatherBadge from '../../components/shipments/ShipmentWeatherBadge';
import WeatherAlertsPanel from '../../components/notifications/WeatherAlertsPanel';
import RoadAlertsPanel from '../../components/notifications/RoadAlertsPanel';

const AIFreightBrokerDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [weather, setWeather] = useState(null);
    const [weatherError, setWeatherError] = useState(null);

    // Mock data
    const [dashboardData, setDashboardData] = useState({
        kpis: {
            totalShipments: 245,
            availableTrucks: 42,
            avgDeliveryTime: '2.5h',
            alerts: {
                delayed: 6,
                etaRisk: 3,
                missingDocs: 2,
                total: 11
            }
        },
        statusBreakdown: {
            onTheWay: 45,
            delivered: 120,
            pendingPickup: 30,
            delayed: 15
        },
        activeShipments: [
            { id: 'SH-001', origin: 'New York', destination: 'Boston', currentLocation: 'New York', status: 'on-the-way', eta: '2h', value: '$12,500', driver: 'John Smith', driverId: 101 },
            { id: 'SH-002', origin: 'Chicago', destination: 'Detroit', currentLocation: 'Chicago', status: 'pending', eta: '4h', value: '$8,200', driver: 'Maria Garcia', driverId: 102 },
            { id: 'SH-003', origin: 'Los Angeles', destination: 'San Francisco', currentLocation: 'San Francisco', status: 'delivered', eta: '0h', value: '$15,800', driver: 'Robert Chen', driverId: 103 },
            { id: 'SH-004', origin: 'Miami', destination: 'Atlanta', currentLocation: 'Miami', status: 'on-the-way', eta: '3h', value: '$9,500', driver: 'Sarah Johnson', driverId: 104 },
            { id: 'SH-005', origin: 'Seattle', destination: 'Portland', currentLocation: 'Seattle', status: 'delayed', eta: '6h', value: '$7,200', driver: 'Mike Davis', driverId: 105 },
        ],
        activeTrucks: [
            { id: 'TRK-001', driver: 'John Smith', status: 'active', shipmentCount: 3, lastPing: '5m ago', utilization: '85%' },
            { id: 'TRK-002', driver: 'Maria Garcia', status: 'active', shipmentCount: 2, lastPing: '2m ago', utilization: '70%' },
            { id: 'TRK-003', driver: 'Robert Chen', status: 'idle', shipmentCount: 1, lastPing: '15m ago', utilization: '45%' },
            { id: 'TRK-004', driver: 'Sarah Johnson', status: 'active', shipmentCount: 4, lastPing: '1m ago', utilization: '92%' },
        ]
    });

    // Fetch weather for each shipment location and send alerts to drivers
    const { getWeatherForShipment, alerts, roadAlerts, combinedAlerts } = useShipmentWeather(dashboardData.activeShipments, {
        autoAlert: true,
        includeRoadAlerts: true
    });

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => {
            setIsRefreshing(false);
        }, 1000);
    };

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                // Get weather for user's registered location (for fleet tracking)
                // NOT current GPS location - the weather should match where the fleet operates
                const userCity = user?.city || user?.address?.city || user?.location?.city || 'Vancouver';
                const response = await axiosClient.get('/api/v1/weather/current', {
                    params: { city: userCity, units: 'metric' },
                });
                setWeather(response.data);
                setWeatherError(null);
            } catch (error) {
                setWeatherError('Weather unavailable');
            }
        };

        fetchWeather();
    }, [user]);

    const handleConfigureMap = () => {
        navigate('/admin/settings?tab=integrations&section=maps');
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'active':
            case 'on-the-way':
            case 'delivered': return '#10b981';
            case 'pending':
            case 'pendingPickup': return '#f59e0b';
            case 'idle':
            case 'delayed': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'active':
            case 'on-the-way':
            case 'delivered': return <CheckCircle size={16} />;
            case 'pending':
            case 'pendingPickup': return <Clock size={16} />;
            case 'idle':
            case 'delayed': return <XCircle size={16} />;
            default: return null;
        }
    };

    const totalStatus = Object.values(dashboardData.statusBreakdown).reduce((a, b) => a + b, 0);

    return (
        <div className="ai-freight-page space-y-5">
            {/* Header and action bar */}
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="text-2xl font-semibold text-white">AI Freight Broker Dashboard</div>
                    <div className="text-sm text-slate-300">
                        Real-time logistics intelligence and monitoring
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15 hover:text-white"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                    >
                        <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
                        {isRefreshing ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>

            {/* Top KPI row */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                {/* Total Shipments */}
                <GlassCard className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/20">
                                <Package size={20} className="text-sky-300" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{dashboardData.kpis.totalShipments}</div>
                                <div className="text-xs text-slate-400">Total Shipments</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1 text-emerald-400">
                            <TrendingUp size={14} />
                            <span className="text-xs font-semibold">+12%</span>
                        </div>
                    </div>
                    <div className="mt-3">
                        <button
                            className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15 hover:text-white"
                            onClick={() => navigate('/ai-bots/freight_broker/shipments')}
                        >
                            View Shipments
                        </button>
                    </div>
                </GlassCard>

                {/* Available Trucks */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20">
                                <Truck size={20} className="text-emerald-400" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{dashboardData.kpis.availableTrucks}</div>
                                <div className="text-xs text-slate-400">Available Trucks</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1 text-rose-400">
                            <TrendingDown size={14} />
                            <span className="text-xs font-semibold">-3%</span>
                        </div>
                    </div>
                </div>

                {/* Average Delivery Time */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/20">
                                <Clock size={20} className="text-amber-400" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{dashboardData.kpis.avgDeliveryTime}</div>
                                <div className="text-xs text-slate-400">Avg Delivery Time</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1 text-emerald-400">
                            <TrendingDown size={14} />
                            <span className="text-xs font-semibold">-8%</span>
                        </div>
                    </div>
                </div>

                {/* Alerts/Exceptions */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/20">
                                <AlertTriangle size={20} className="text-rose-400" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{dashboardData.kpis.alerts.total}</div>
                                <div className="text-xs text-slate-400">Active Alerts</div>
                            </div>
                        </div>
                        <div className="rounded-full border border-rose-400/40 bg-rose-500/10 px-2 py-0.5 text-xs font-semibold text-rose-200">
                            Critical
                        </div>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                        <div className="text-slate-300">
                            <span className="text-rose-400 font-semibold">{dashboardData.kpis.alerts.delayed}</span> Delayed
                        </div>
                        <div className="text-slate-300">
                            <span className="text-amber-400 font-semibold">{dashboardData.kpis.alerts.etaRisk}</span> ETA Risk
                        </div>
                    </div>
                </div>
            </div>

            {/* Weather Snapshot */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/20">
                            <MapPin size={20} className="text-cyan-400" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-white">
                                {weather?.temp != null ? `${Math.round(weather.temp)}°C` : '--'}
                            </div>
                            <div className="text-xs text-slate-400">Weather</div>
                        </div>
                    </div>
                    <div className="text-right text-xs text-slate-400">
                        <div>{weather?.location?.name || 'Riyadh'}</div>
                        <div>{weather?.description || weatherError || 'Loading...'}</div>
                    </div>
                </div>
            </div>

            {/* Second row - Status Breakdown and Active Shipments */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-[300px_minmax(0,1fr)]">
                {/* Status Breakdown */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="text-sm font-semibold text-white mb-4">Shipment Status Breakdown</div>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="h-3 w-3 rounded-full bg-emerald-500"></div>
                                <span className="text-sm text-slate-300">On The Way</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-white">{dashboardData.statusBreakdown.onTheWay}</span>
                                <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-emerald-500 rounded-full"
                                        style={{ width: `${(dashboardData.statusBreakdown.onTheWay / totalStatus) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="h-3 w-3 rounded-full bg-sky-500"></div>
                                <span className="text-sm text-slate-300">Delivered</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-white">{dashboardData.statusBreakdown.delivered}</span>
                                <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-sky-500 rounded-full"
                                        style={{ width: `${(dashboardData.statusBreakdown.delivered / totalStatus) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="h-3 w-3 rounded-full bg-amber-500"></div>
                                <span className="text-sm text-slate-300">Pending Pickup</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-white">{dashboardData.statusBreakdown.pendingPickup}</span>
                                <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-amber-500 rounded-full"
                                        style={{ width: `${(dashboardData.statusBreakdown.pendingPickup / totalStatus) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="h-3 w-3 rounded-full bg-rose-500"></div>
                                <span className="text-sm text-slate-300">Delayed</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-white">{dashboardData.statusBreakdown.delayed}</span>
                                <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-rose-500 rounded-full"
                                        style={{ width: `${(dashboardData.statusBreakdown.delayed / totalStatus) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Active Shipments */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between mb-4">
                        <div className="text-sm font-semibold text-white">Active Shipments</div>
                        <button
                            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/ai-bots/freight_broker/shipments')}
                        >
                            View All
                        </button>
                    </div>
                    <div className="space-y-2">
                        {dashboardData.activeShipments.map((shipment) => (
                            <div key={shipment.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-950/60 p-3 hover:bg-white/10">
                                <div className="flex items-center gap-3">
                                    <div className={`h-2 w-2 rounded-full ${shipment.status === 'delivered' ? 'bg-emerald-500' :
                                        shipment.status === 'on-the-way' ? 'bg-sky-500' :
                                            shipment.status === 'pending' ? 'bg-amber-500' : 'bg-rose-500'
                                        }`}></div>
                                    <div>
                                        <div className="text-sm font-semibold text-white">{shipment.id}</div>
                                        <div className="text-xs text-slate-400 flex items-center gap-2">
                                            <span>{shipment.origin} → {shipment.destination}</span>
                                            <ShipmentWeatherBadge weather={getWeatherForShipment(shipment)} location={shipment.currentLocation} />
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-semibold text-white">{shipment.value}</div>
                                    <div className="text-xs text-slate-400">ETA: {shipment.eta}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Third row - Active Trucks and Quick Actions */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
                {/* Active Trucks */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="flex items-center justify-between mb-4">
                        <div className="text-sm font-semibold text-white">Active Trucks</div>
                        <button
                            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/dispatch')}
                        >
                            Fleet View
                        </button>
                    </div>
                    <div className="space-y-2">
                        {dashboardData.activeTrucks.map((truck) => (
                            <div key={truck.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-950/60 p-3 hover:bg-white/10">
                                <div className="flex items-center gap-3">
                                    <div className={`h-2 w-2 rounded-full ${truck.status === 'active' ? 'bg-emerald-500' : 'bg-slate-500'
                                        }`}></div>
                                    <div>
                                        <div className="text-sm font-semibold text-white">{truck.id}</div>
                                        <div className="text-xs text-slate-400">{truck.driver}</div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-semibold text-white">{truck.utilization}</div>
                                    <div className="text-xs text-slate-400">{truck.lastPing}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                    <div className="text-sm font-semibold text-white mb-4">Quick Actions</div>
                    <div className="space-y-2">
                        <button
                            className="w-full rounded-lg border border-white/10 bg-white/5 p-3 text-left text-sm font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/ai-bots/freight_broker/shipments')}
                        >
                            <div className="flex items-center gap-2">
                                <Package size={16} />
                                New Shipment
                            </div>
                        </button>
                        <button
                            className="w-full rounded-lg border border-white/10 bg-white/5 p-3 text-left text-sm font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/ai-bots/freight_broker/map')}
                        >
                            <div className="flex items-center gap-2">
                                <MapPin size={16} />
                                View Map
                            </div>
                        </button>
                        <button
                            className="w-full rounded-lg border border-white/10 bg-white/5 p-3 text-left text-sm font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/reports')}
                        >
                            <div className="flex items-center gap-2">
                                <BarChart3 size={16} />
                                Analytics
                            </div>
                        </button>
                        <button
                            className="w-full rounded-lg border border-white/10 bg-white/5 p-3 text-left text-sm font-semibold text-white hover:bg-white/10"
                            onClick={() => navigate('/alerts')}
                        >
                            <div className="flex items-center gap-2">
                                <AlertTriangle size={16} />
                                Alerts Center
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            {/* Weather Alerts Section */}
            {alerts && alerts.length > 0 && (
                <div className="mt-4">
                    <WeatherAlertsPanel alerts={alerts} />
                </div>
            )}

            {/* Road Alerts Section */}
            {(roadAlerts && roadAlerts.length > 0 || combinedAlerts && combinedAlerts.length > 0) && (
                <div className="mt-4">
                    <RoadAlertsPanel roadAlerts={roadAlerts} combinedAlerts={combinedAlerts} />
                </div>
            )}
        </div >
    );
};

export default AIFreightBrokerDashboard;
