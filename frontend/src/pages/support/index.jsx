/**
 * Support Pages
 * Main support pages
 */

import React from 'react';
import { SupportTicketList, SupportTicketCreate, SupportTicketDetail } from '../../components/SupportTickets';
import { KnowledgeBaseList, KnowledgeBaseArticle, CreateKnowledgeBaseArticle } from '../../components/KnowledgeBase';
import { AgentDashboard, AgentTicketDetail } from '../../components/AgentDashboard';
import RequireAuth from '../../components/RequireAuth';
import { useParams } from 'react-router-dom';

// ============================================
// CUSTOMER PAGES
// ============================================

export function SupportPage() {
    return (
        <RequireAuth>
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <SupportTicketList />
                </div>
            </div>
        </RequireAuth>
    );
}

export function CreateTicketPage() {
    return (
        <RequireAuth>
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <SupportTicketCreate />
                </div>
            </div>
        </RequireAuth>
    );
}

export function TicketDetailPage() {
    const { ticketId } = useParams();

    return (
        <RequireAuth>
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <SupportTicketDetail key={ticketId} />
                </div>
            </div>
        </RequireAuth>
    );
}

export function KnowledgeBasePage() {
    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <KnowledgeBaseList />
        </div>
    );
}

export function KnowledgeBaseArticlePage() {
    const { articleId } = useParams();

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4">
                <KnowledgeBaseArticle key={articleId} />
            </div>
        </div>
    );
}

// ============================================
// AGENT PAGES
// ============================================

export function AgentDashboardPage() {
    return (
        <RequireAuth requiredRole="agent">
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <AgentDashboard />
                </div>
            </div>
        </RequireAuth>
    );
}

export function AgentTicketPage() {
    const { ticketId } = useParams();

    return (
        <RequireAuth requiredRole="agent">
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <AgentTicketDetail ticketId={ticketId} />
                </div>
            </div>
        </RequireAuth>
    );
}

// ============================================
// ADMIN PAGES
// ============================================

export function CreateArticlePage() {
    return (
        <RequireAuth requiredRole="admin">
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <CreateKnowledgeBaseArticle />
                </div>
            </div>
        </RequireAuth>
    );
}

export function SupportAdminDashboard() {
    const [stats, setStats] = React.useState(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await fetch('/api/v1/support/stats');
            setStats(await response.json());
        } catch (error) {
            console.error('Error fetching stats:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center py-8">Loading...</div>;

    return (
        <RequireAuth requiredRole="admin">
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4">
                    <h1 className="text-3xl font-bold mb-8">Support Admin Dashboard</h1>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <StatCard
                            icon="📋"
                            label="Total Tickets"
                            value={stats?.total_tickets || 0}
                        />
                        <StatCard
                            icon="⏳"
                            label="Open Tickets"
                            value={stats?.open_tickets || 0}
                        />
                        <StatCard
                            icon="✅"
                            label="Resolved Today"
                            value={stats?.resolved_today || 0}
                        />
                        <StatCard
                            icon="⚠️"
                            label="At Risk (SLA)"
                            value={stats?.at_risk_count || 0}
                        />
                    </div>

                    {/* Charts */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-bold mb-4">Ticket Distribution by Status</h2>
                            <div className="h-64 bg-gradient-to-r from-blue-100 to-blue-200 rounded flex items-center justify-center">
                                <p className="text-gray-500">Chart placeholder</p>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-bold mb-4">Average Response Time</h2>
                            <div className="h-64 bg-gradient-to-r from-green-100 to-green-200 rounded flex items-center justify-center">
                                <p className="text-gray-500">Chart placeholder</p>
                            </div>
                        </div>
                    </div>

                    {/* Agent Performance */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-bold mb-4">Agent Performance</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-100">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Agent</th>
                                        <th className="px-4 py-3 text-left">Resolved</th>
                                        <th className="px-4 py-3 text-left">Avg Response Time</th>
                                        <th className="px-4 py-3 text-left">Satisfaction</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {/* Agent rows would go here */}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </RequireAuth>
    );
}

function StatCard({ icon, label, value }) {
    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-600 text-sm">{label}</p>
                    <p className="text-3xl font-bold">{value}</p>
                </div>
                <div className="text-4xl">{icon}</div>
            </div>
        </div>
    );
}
