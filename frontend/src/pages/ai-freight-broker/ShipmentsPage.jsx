import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
    Package,
    Plus,
    Search,
    Filter,
    Eye,
    Edit,
    Trash2,
    MapPin,
    Clock,
    DollarSign,
    Truck,
    CheckCircle,
    XCircle,
    AlertTriangle
} from 'lucide-react';
import GlassCard from '../../components/ui/GlassCard';
import { useShipmentWeather } from '../../hooks/useShipmentWeather';
import ShipmentWeatherBadge from '../../components/shipments/ShipmentWeatherBadge';

const ShipmentsPage = ({ mode }) => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const isNewMode = mode === 'new' || searchParams.get('new') === 'true';

    const [shipments, setShipments] = useState([
        {
            id: 'SH-001',
            origin: 'New York, NY',
            destination: 'Boston, MA',
            currentLocation: 'Hartford',
            status: 'on-the-way',
            eta: '2h 30m',
            value: '$12,500',
            truck: 'TRK-001',
            driver: 'John Smith',
            driverId: 101,
            createdAt: '2024-01-15',
            priority: 'high'
        },
        {
            id: 'SH-002',
            origin: 'Chicago, IL',
            destination: 'Detroit, MI',
            currentLocation: 'Chicago',
            status: 'pending',
            eta: '4h 15m',
            value: '$8,200',
            truck: 'TRK-002',
            driver: 'Maria Garcia',
            driverId: 102,
            createdAt: '2024-01-15',
            priority: 'medium'
        },
        {
            id: 'SH-003',
            origin: 'Los Angeles, CA',
            destination: 'San Francisco, CA',
            currentLocation: 'San Francisco',
            status: 'delivered',
            eta: '0h',
            value: '$15,800',
            truck: 'TRK-003',
            driver: 'Robert Chen',
            driverId: 103,
            createdAt: '2024-01-14',
            priority: 'low'
        },
        {
            id: 'SH-004',
            origin: 'Miami, FL',
            destination: 'Atlanta, GA',
            currentLocation: 'Jacksonville',
            status: 'on-the-way',
            eta: '3h 45m',
            value: '$9,500',
            truck: 'TRK-004',
            driver: 'Sarah Johnson',
            driverId: 104,
            createdAt: '2024-01-15',
            priority: 'medium'
        },
        {
            id: 'SH-005',
            origin: 'Seattle, WA',
            destination: 'Portland, OR',
            currentLocation: 'Tacoma',
            status: 'delayed',
            eta: '6h 20m',
            value: '$7,200',
            truck: 'TRK-005',
            driver: 'Mike Davis',
            driverId: 105,
            createdAt: '2024-01-13',
            priority: 'high'
        }
    ]);

    // Fetch weather for each shipment location
    const { getWeatherForShipment } = useShipmentWeather(shipments);

    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');

    const filteredShipments = shipments.filter(shipment => {
        const matchesSearch = shipment.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.driver.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || shipment.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

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

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'high': return '#ef4444';
            case 'medium': return '#f59e0b';
            case 'low': return '#10b981';
            default: return '#6b7280';
        }
    };

    if (isNewMode) {
        return (
            <div className="ai-freight-page space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <div className="text-2xl font-semibold text-white">Create New Shipment</div>
                        <div className="text-sm text-slate-300">
                            Fill in the details to create a new freight shipment
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15 hover:text-white"
                            onClick={() => navigate('/ai-bots/freight_broker/shipments')}
                        >
                            Cancel
                        </button>
                        <button className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15 hover:text-white">
                            Create Shipment
                        </button>
                    </div>
                </div>

                <GlassCard className="border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
                    <form className="space-y-6">
                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-slate-200">Origin</label>
                                <input
                                    type="text"
                                    placeholder="City, State"
                                    className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-slate-100 placeholder-slate-500"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-slate-200">Destination</label>
                                <input
                                    type="text"
                                    placeholder="City, State"
                                    className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-slate-100 placeholder-slate-500"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-slate-200">Value</label>
                                <input
                                    type="text"
                                    placeholder="$0.00"
                                    className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-slate-100 placeholder-slate-500"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-slate-200">Priority</label>
                                <select className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-slate-100">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-200">Notes</label>
                            <textarea
                                placeholder="Additional shipment notes..."
                                rows={4}
                                className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-sm text-slate-100 placeholder-slate-500"
                            ></textarea>
                        </div>
                    </form>
                </GlassCard>
            </div>
        );
    }

    return (
        <div className="ai-freight-page space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="text-2xl font-semibold text-white">Shipments Management</div>
                    <div className="text-sm text-slate-300">
                        Track and manage all freight shipments
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:bg-white/15 hover:text-white"
                        onClick={() => navigate('/ai-bots/freight_broker/map')}
                    >
                        <MapPin size={14} />
                        View Map
                    </button>
                    <button
                        className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/15"
                        onClick={() => navigate('/ai-bots/freight_broker/shipments?new=true')}
                    >
                        <Plus size={14} />
                        New Shipment
                    </button>
                </div>
            </div>

            {/* Search filters */}
            <GlassCard className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-2 flex-1 min-w-[200px]">
                        <Search size={16} className="text-slate-300" />
                        <input
                            type="text"
                            placeholder="Search shipments..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="flex-1 bg-transparent border-none text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
                        />
                    </div>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs text-slate-100"
                    >
                        <option value="all">All Status</option>
                        <option value="pending">Pending</option>
                        <option value="on-the-way">On The Way</option>
                        <option value="delivered">Delivered</option>
                        <option value="delayed">Delayed</option>
                    </select>
                </div>
            </GlassCard>

            {/* Shipments table */}
            <GlassCard className="border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">ID</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">Route</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">Status</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">ETA</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">Value</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">Driver</th>
                                <th className="text-left py-3 px-2 text-slate-400 font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredShipments.map((shipment) => (
                                <tr key={shipment.id} className="border-b border-white/10 hover:bg-white/5">
                                    <td className="py-3 px-2">
                                        <span className="font-mono text-sky-400 font-semibold">{shipment.id}</span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <div className="flex flex-col gap-1">
                                            <div className="flex items-center gap-2">
                                                <MapPin size={14} className="text-slate-400" />
                                                <span className="text-white font-semibold">{shipment.origin}</span>
                                                <span className="text-slate-400">→</span>
                                                <span className="text-white font-semibold">{shipment.destination}</span>
                                            </div>
                                            <div className="flex items-center gap-2 ml-5">
                                                <span className="text-xs text-sky-400">Current: {shipment.currentLocation}</span>
                                                <ShipmentWeatherBadge weather={getWeatherForShipment(shipment)} />
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-3 px-2">
                                        <span className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold ${shipment.status === 'delivered' ? 'border-emerald-400/40 bg-emerald-500/10 text-emerald-200' :
                                            shipment.status === 'on-the-way' ? 'border-sky-400/40 bg-sky-500/10 text-sky-200' :
                                                shipment.status === 'pending' ? 'border-amber-400/40 bg-amber-500/10 text-amber-200' :
                                                    'border-rose-400/40 bg-rose-500/10 text-rose-200'
                                            }`}>
                                            {shipment.status.replace('-', ' ')}
                                        </span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <div className="flex items-center gap-1">
                                            <Clock size={14} className="text-slate-400" />
                                            <span className="text-white">{shipment.eta}</span>
                                        </div>
                                    </td>
                                    <td className="py-3 px-2">
                                        <span className="text-emerald-400 font-semibold">{shipment.value}</span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <div>
                                            <div className="text-white font-semibold">{shipment.driver}</div>
                                            <div className="text-xs text-slate-400">{shipment.truck}</div>
                                        </div>
                                    </td>
                                    <td className="py-3 px-2">
                                        <div className="flex items-center gap-1">
                                            <button className="p-1 rounded border border-white/15 bg-white/10 text-slate-100 hover:bg-white/15 hover:text-white">
                                                <Eye size={14} />
                                            </button>
                                            <button className="p-1 rounded border border-white/15 bg-white/10 text-slate-100 hover:bg-white/15 hover:text-white">
                                                <Edit size={14} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </GlassCard>
        </div>
    );
};

export default ShipmentsPage;
