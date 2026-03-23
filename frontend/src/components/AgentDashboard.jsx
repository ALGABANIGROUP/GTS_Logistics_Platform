/**
 * Support Agent Dashboard
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';

// ============================================
// AGENT DASHBOARD
// ============================================

export function AgentDashboard() {
    const [tickets, setTickets] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('assigned');

    useEffect(() => {
        fetchDashboardData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, [filter]);

    const fetchDashboardData = async () => {
        try {
            const params = { status: filter };
            const [ticketsRes, statsRes] = await Promise.all([
                axiosClient.get('/api/v1/support/tickets/agent/assigned', { params }),
                axiosClient.get('/api/v1/support/stats/agent/me')
            ]);
            setTickets(ticketsRes.data);
            setStats(statsRes.data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const getUrgencyIndicator = (priority, slaStatus) => {
        if (slaStatus === 'breached') return 'BR';
        if (slaStatus === 'at_risk') return 'RSK';
        if (priority === 'critical') return 'CRT';
        return 'OK';
    };

    if (loading) return <div className="text-center py-8">Loading dashboard...</div>;

    return (
        <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    icon="TCK"
                    label="Assigned Tickets"
                    value={stats?.assigned_count || 0}
                    color="bg-blue-100 text-blue-800"
                />
                <StatCard
                    icon="RUN"
                    label="In Progress"
                    value={stats?.in_progress_count || 0}
                    color="bg-purple-100 text-purple-800"
                />
                <StatCard
                    icon="OK"
                    label="Resolved Today"
                    value={stats?.resolved_today || 0}
                    color="bg-green-100 text-green-800"
                />
                <StatCard
                    icon="SAT"
                    label="Avg Satisfaction"
                    value={`${(stats?.avg_satisfaction || 0).toFixed(1)}/5`}
                    color="bg-yellow-100 text-yellow-800"
                />
            </div>

            {/* Main Content */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold">My Tickets</h2>
                    <div className="flex gap-2">
                        {['assigned', 'in_progress', 'waiting_customer'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilter(status)}
                                className={`px-4 py-2 rounded-lg font-medium ${filter === status
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                    }`}
                            >
                                {status.replace('_', ' ').toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Tickets Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-100 border-b-2">
                            <tr>
                                <th className="px-4 py-3 text-left">Status</th>
                                <th className="px-4 py-3 text-left">Ticket</th>
                                <th className="px-4 py-3 text-left">Customer</th>
                                <th className="px-4 py-3 text-left">Priority</th>
                                <th className="px-4 py-3 text-left">Updated</th>
                                <th className="px-4 py-3 text-left">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickets.map(ticket => (
                                <tr key={ticket.id} className="border-b hover:bg-gray-50">
                                    <td className="px-4 py-3">
                                        {getUrgencyIndicator(ticket.priority, ticket.sla_status)}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="font-mono font-bold text-blue-600">{ticket.ticket_number}</div>
                                        <div className="text-sm text-gray-600 truncate">{ticket.title}</div>
                                    </td>
                                    <td className="px-4 py-3 text-sm">{ticket.customer_name}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 rounded text-xs font-bold text-white ${ticket.priority === 'critical' ? 'bg-red-600' :
                                            ticket.priority === 'high' ? 'bg-orange-600' :
                                                ticket.priority === 'medium' ? 'bg-yellow-600' :
                                                    'bg-green-600'
                                            }`}>
                                            {ticket.priority.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600">
                                        {new Date(ticket.updated_at).toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3">
                                        <button className="text-blue-600 hover:text-blue-800 font-medium">
                                            View {'>'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {tickets.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                        No {filter} tickets
                    </div>
                )}
            </div>

            {/* Performance Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PerformanceChart stats={stats} />
                <SLAComplianceChart stats={stats} />
            </div>
        </div>
    );
}

// ============================================
// STAT CARD COMPONENT
// ============================================

function StatCard({ icon, label, value, color }) {
    return (
        <div className={`${color} rounded-lg p-6 text-center`}>
            <div className="text-3xl mb-2">{icon}</div>
            <p className="text-sm opacity-75">{label}</p>
            <p className="text-2xl font-bold">{value}</p>
        </div>
    );
}

// ============================================
// PERFORMANCE CHART
// ============================================

function PerformanceChart({ stats }) {
    const data = [
        { name: 'Resolved', value: stats?.resolved_count || 0 },
        { name: 'Pending', value: stats?.in_progress_count || 0 },
        { name: 'Waiting', value: stats?.waiting_customer_count || 0 },
    ];

    const maxValue = Math.max(...data.map(d => d.value)) || 1;

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-6">Performance This Month</h3>
            <div className="space-y-4">
                {data.map(item => (
                    <div key={item.name}>
                        <div className="flex justify-between mb-2">
                            <span className="font-medium">{item.name}</span>
                            <span className="font-bold text-blue-600">{item.value}</span>
                        </div>
                        <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div
                                className="bg-blue-600 h-full rounded-full transition-all duration-300"
                                style={{ width: `${(item.value / maxValue) * 100}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ============================================
// SLA COMPLIANCE CHART
// ============================================

function SLAComplianceChart({ stats }) {
    const compliantPercent = stats?.sla_compliance_rate || 0;
    const breachedPercent = 100 - compliantPercent;

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-6">SLA Compliance</h3>
            <div className="flex items-center justify-center gap-8">
                <div className="text-center">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-r from-green-400 to-green-600 flex items-center justify-center">
                        <div className="text-white text-2xl font-bold">{compliantPercent.toFixed(0)}%</div>
                    </div>
                    <p className="mt-3 font-medium">Compliant</p>
                </div>
                <div>
                    <div className="flex items-center gap-2 mb-4">
                        <div className="w-4 h-4 bg-green-600 rounded"></div>
                        <span className="text-gray-700">On Time: {compliantPercent.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-red-600 rounded"></div>
                        <span className="text-gray-700">Breached: {breachedPercent.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ============================================
// AGENT TICKET DETAIL (Editing View)
// ============================================

export function AgentTicketDetail({ ticketId }) {
    const [ticket, setTicket] = useState(null);
    const [status, setStatus] = useState('');
    const [internalNote, setInternalNote] = useState('');
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        fetchTicket();
    }, [ticketId]);

    const fetchTicket = async () => {
        try {
            const response = await axiosClient.get(`/api/v1/support/tickets/${ticketId}`);
            setTicket(response.data);
            setStatus(response.data.status);
        } catch (error) {
            console.error('Error fetching ticket:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusChange = async (newStatus) => {
        try {
            setUpdating(true);
            await axiosClient.put(`/api/v1/support/tickets/${ticketId}/status`, {
                status: newStatus,
                internal_note: internalNote || undefined
            });
            setStatus(newStatus);
            setInternalNote('');
            fetchTicket();
        } catch (error) {
            console.error('Error updating ticket:', error);
            alert('Failed to update ticket');
        } finally {
            setUpdating(false);
        }
    };

    if (loading) return <div className="text-center py-8">Loading...</div>;
    if (!ticket) return <div className="text-center py-8 text-red-600">Ticket not found</div>;

    return (
        <div className="grid grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="col-span-2 space-y-6">
                {/* Ticket Info */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-2xl font-bold mb-4">{ticket.title}</h2>
                    <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div>
                            <p className="text-gray-600">Ticket Number</p>
                            <p className="font-mono font-bold">{ticket.ticket_number}</p>
                        </div>
                        <div>
                            <p className="text-gray-600">Category</p>
                            <p className="font-medium">{ticket.category}</p>
                        </div>
                        <div>
                            <p className="text-gray-600">Customer</p>
                            <p className="font-medium">{ticket.customer_name}</p>
                        </div>
                        <div>
                            <p className="text-gray-600">Created</p>
                            <p className="font-medium">{new Date(ticket.created_at).toLocaleString()}</p>
                        </div>
                    </div>
                    <div className="border-t pt-4">
                        <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
                    </div>
                </div>

                {/* Internal Notes */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold mb-4">Internal Notes (Not visible to customer)</h3>
                    <textarea
                        value={internalNote}
                        onChange={(e) => setInternalNote(e.target.value)}
                        rows="4"
                        placeholder="Add internal notes..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
                {/* Status Update */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold mb-4">Update Status</h3>
                    <div className="space-y-2">
                        {['in_progress', 'waiting_customer', 'resolved', 'closed'].map(s => (
                            <button
                                key={s}
                                onClick={() => handleStatusChange(s)}
                                disabled={updating}
                                className={`w-full px-4 py-2 rounded-lg font-medium transition ${status === s
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                    }`}
                            >
                                {s.replace('_', ' ').toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>

                {/* SLA Info */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold mb-4">SLA Status</h3>
                    <div className="space-y-3">
                        <div>
                            <p className="text-sm text-gray-600">Response Time</p>
                            <p className={`font-bold ${new Date(ticket.sla_response_due) > new Date() ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {new Date(ticket.sla_response_due).toLocaleTimeString()}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Resolution Due</p>
                            <p className={`font-bold ${new Date(ticket.sla_resolution_due) > new Date() ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {new Date(ticket.sla_resolution_due).toLocaleString()}
                            </p>
                        </div>
                        <div className="pt-3 border-t">
                            <p className={`px-3 py-1 rounded-full text-sm font-bold text-center ${ticket.sla_status === 'compliant' ? 'bg-green-100 text-green-800' :
                                ticket.sla_status === 'at_risk' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-red-100 text-red-800'
                                }`}>
                                {ticket.sla_status.toUpperCase()}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
                    <div className="space-y-2">
                        <button className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                            Send Email to Customer
                        </button>
                        <button className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
                            Escalate to Manager
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
