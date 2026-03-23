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

const ShipmentsPage = ({ mode }) => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const isNewMode = mode === 'new' || searchParams.get('new') === 'true';

    const [shipments, setShipments] = useState([
        {
            id: 'SH-001',
            origin: 'New York, NY',
            destination: 'Boston, MA',
            status: 'on-the-way',
            eta: '2h 30m',
            value: '$12,500',
            truck: 'TRK-001',
            driver: 'John Smith',
            createdAt: '2024-01-15',
            priority: 'high'
        },
        {
            id: 'SH-002',
            origin: 'Chicago, IL',
            destination: 'Detroit, MI',
            status: 'pending',
            eta: '4h 15m',
            value: '$8,200',
            truck: 'TRK-002',
            driver: 'Maria Garcia',
            createdAt: '2024-01-15',
            priority: 'medium'
        },
        {
            id: 'SH-003',
            origin: 'Los Angeles, CA',
            destination: 'San Francisco, CA',
            status: 'delivered',
            eta: '0h 0m',
            value: '$15,800',
            truck: 'TRK-003',
            driver: 'Robert Chen',
            createdAt: '2024-01-14',
            priority: 'high'
        },
    ]);

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
            case 'delivered': return '#10b981';
            case 'on-the-way': return '#3b82f6';
            case 'pending': return '#f59e0b';
            case 'delayed': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'delivered': return <CheckCircle size={16} />;
            case 'on-the-way': return <Truck size={16} />;
            case 'pending': return <Clock size={16} />;
            case 'delayed': return <AlertTriangle size={16} />;
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
            <div className="shipments-page">
                <div className="page-header">
                    <div className="header-left">
                        <h1>Create New Shipment</h1>
                        <p>Fill in the details to create a new freight shipment</p>
                    </div>
                    <div className="header-actions">
                        <button
                            className="glass-button secondary"
                            onClick={() => navigate('/ai-freight-broker/shipments')}
                        >
                            Cancel
                        </button>
                        <button className="glass-button primary">
                            Create Shipment
                        </button>
                    </div>
                </div>

                <GlassCard className="new-shipment-form">
                    <form className="shipment-form">
                        <div className="form-grid">
                            <div className="form-group">
                                <label>Origin</label>
                                <input type="text" placeholder="City, State" />
                            </div>
                            <div className="form-group">
                                <label>Destination</label>
                                <input type="text" placeholder="City, State" />
                            </div>
                            <div className="form-group">
                                <label>Value</label>
                                <input type="text" placeholder="$0.00" />
                            </div>
                            <div className="form-group">
                                <label>Priority</label>
                                <select>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                        </div>
                        <div className="form-group full-width">
                            <label>Notes</label>
                            <textarea placeholder="Additional shipment notes..." rows={4}></textarea>
                        </div>
                    </form>
                </GlassCard>
            </div>
        );
    }

    return (
        <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div className="text-2xl font-semibold text-white">Shipments Management</div>
                    <div className="text-sm text-slate-300">
                        Track and manage all freight shipments
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/15"
                        onClick={() => navigate('/ai-freight-broker/map')}
                    >
                        <MapPin size={14} />
                        View Map
                    </button>
                    <button
                        className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/15"
                        onClick={() => navigate('/ai-freight-broker/shipments?new=true')}
                    >
                        <Plus size={14} />
                        New Shipment
                    </button>
                </div>
            </div>

            {/* Filters and Search */}
            <GlassCard className="filters-card">
                <div className="filters-content">
                    <div className="search-group">
                        <Search size={20} />
                        <input
                            type="text"
                            placeholder="Search shipments..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="filter-group">
                        <Filter size={20} />
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                        >
                            <option value="all">All Status</option>
                            <option value="pending">Pending</option>
                            <option value="on-the-way">On The Way</option>
                            <option value="delivered">Delivered</option>
                            <option value="delayed">Delayed</option>
                        </select>
                    </div>
                </div>
            </GlassCard>

            {/* Shipments Table */}
            <GlassCard className="shipments-table-card">
                <div className="table-container">
                    <table className="shipments-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Route</th>
                                <th>Status</th>
                                <th>ETA</th>
                                <th>Value</th>
                                <th>Truck</th>
                                <th>Driver</th>
                                <th>Priority</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredShipments.map((shipment) => (
                                <tr key={shipment.id}>
                                    <td className="shipment-id">{shipment.id}</td>
                                    <td>
                                        <div className="route-cell">
                                            <MapPin size={16} />
                                            <span>{shipment.origin} → {shipment.destination}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <span
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(shipment.status) }}
                                        >
                                            {getStatusIcon(shipment.status)}
                                            {shipment.status.replace('-', ' ')}
                                        </span>
                                    </td>
                                    <td>{shipment.eta}</td>
                                    <td className="value-cell">
                                        <DollarSign size={14} />
                                        {shipment.value}
                                    </td>
                                    <td>{shipment.truck}</td>
                                    <td>{shipment.driver}</td>
                                    <td>
                                        <span
                                            className="priority-badge"
                                            style={{ backgroundColor: getPriorityColor(shipment.priority) }}
                                        >
                                            {shipment.priority}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="actions-cell">
                                            <button className="action-btn view">
                                                <Eye size={14} />
                                            </button>
                                            <button className="action-btn edit">
                                                <Edit size={14} />
                                            </button>
                                            <button className="action-btn delete">
                                                <Trash2 size={14} />
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