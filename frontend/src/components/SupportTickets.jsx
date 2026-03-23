/**
 * Support System Frontend Components
 * Frontend support interface components
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';

// ============================================
// TICKET LIST COMPONENT - Ticket list
// ============================================

export function SupportTicketList() {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const navigate = useNavigate();

    useEffect(() => {
        fetchTickets();
    }, [filter]);

    const fetchTickets = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filter !== 'all') params.status = filter;

            const response = await axiosClient.get('/api/v1/support/tickets', { params });
            setTickets(response.data);
        } catch (error) {
            console.error('Error fetching tickets:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const statusColors = {
            'open': 'bg-red-100 text-red-800',
            'in_progress': 'bg-blue-100 text-blue-800',
            'waiting_customer': 'bg-yellow-100 text-yellow-800',
            'resolved': 'bg-green-100 text-green-800',
            'closed': 'bg-gray-100 text-gray-800',
        };

        return <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[status] || 'bg-gray-100'}`}>
            {status.replace('_', ' ').toUpperCase()}
        </span>;
    };

    const getPriorityBadge = (priority) => {
        const priorityColors = {
            'critical': 'bg-red-500 text-white',
            'high': 'bg-orange-500 text-white',
            'medium': 'bg-yellow-500 text-white',
            'low': 'bg-green-500 text-white',
        };

        return <span className={`px-2 py-1 rounded text-xs font-bold ${priorityColors[priority] || 'bg-gray-500'}`}>
            {priority.toUpperCase()}
        </span>;
    };

    if (loading) return <div className="text-center py-8">Loading tickets...</div>;

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Support Tickets</h2>
                <button
                    onClick={() => navigate('/support/tickets/create')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                    Create Ticket
                </button>
            </div>

            {/* Filter Buttons */}
            <div className="flex gap-2 mb-6 flex-wrap">
                {['all', 'open', 'in_progress', 'resolved', 'closed'].map(status => (
                    <button
                        key={status}
                        onClick={() => setFilter(status)}
                        className={`px-4 py-2 rounded-lg font-medium ${filter === status
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                    >
                        {status === 'all' ? 'All' : status.replace('_', ' ').toUpperCase()}
                    </button>
                ))}
            </div>

            {/* Tickets Table */}
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-100 border-b-2 border-gray-300">
                        <tr>
                            <th className="px-4 py-3 text-left">Ticket #</th>
                            <th className="px-4 py-3 text-left">Title</th>
                            <th className="px-4 py-3 text-left">Status</th>
                            <th className="px-4 py-3 text-left">Priority</th>
                            <th className="px-4 py-3 text-left">Created</th>
                            <th className="px-4 py-3 text-left">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tickets.map(ticket => (
                            <tr key={ticket.id} className="border-b hover:bg-gray-50">
                                <td className="px-4 py-3 font-mono font-bold text-blue-600">
                                    {ticket.ticket_number}
                                </td>
                                <td className="px-4 py-3">{ticket.title}</td>
                                <td className="px-4 py-3">{getStatusBadge(ticket.status)}</td>
                                <td className="px-4 py-3">{getPriorityBadge(ticket.priority)}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">
                                    {new Date(ticket.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-4 py-3">
                                    <button
                                        onClick={() => navigate(`/support/tickets/${ticket.id}`)}
                                        className="text-blue-600 hover:text-blue-800 font-medium"
                                    >
                                        View
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {tickets.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    No tickets found
                </div>
            )}
        </div>
    );
}

// ============================================
// TICKET CREATE COMPONENT - Create ticket
// ============================================

export function SupportTicketCreate() {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: 'general',
        priority: 'medium',
    });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            const response = await axiosClient.post('/api/v1/support/tickets', formData);
            navigate(`/support/tickets/${response.data.id}`);
        } catch (error) {
            console.error('Error creating ticket:', error);
            alert('Failed to create ticket');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Create Support Ticket</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Title */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Title *
                    </label>
                    <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Brief description of your issue"
                    />
                </div>

                {/* Description */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description *
                    </label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                        rows="6"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Detailed description of your issue"
                    />
                </div>

                {/* Category */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category *
                    </label>
                    <select
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="technical">Technical Support</option>
                        <option value="billing">Billing</option>
                        <option value="account">Account</option>
                        <option value="general">General</option>
                        <option value="bug_report">Bug Report</option>
                        <option value="feature_request">Feature Request</option>
                    </select>
                </div>

                {/* Priority */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Priority *
                    </label>
                    <select
                        name="priority"
                        value={formData.priority}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>

                {/* Buttons */}
                <div className="flex gap-3 pt-4">
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? 'Creating...' : 'Create Ticket'}
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/support/tickets')}
                        className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}

// ============================================
// TICKET DETAIL COMPONENT - Ticket details
// ============================================

export function SupportTicketDetail() {
    const { ticketId } = useParams();
    const [ticket, setTicket] = useState(null);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchTicketDetails();
    }, [ticketId]);

    const fetchTicketDetails = async () => {
        try {
            setLoading(true);
            const [ticketRes, commentsRes] = await Promise.all([
                axiosClient.get(`/api/v1/support/tickets/${ticketId}`),
                axiosClient.get(`/api/v1/support/tickets/${ticketId}/comments`)
            ]);
            setTicket(ticketRes.data);
            setComments(commentsRes.data);
        } catch (error) {
            console.error('Error fetching ticket:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddComment = async (e) => {
        e.preventDefault();
        try {
            setSubmitting(true);
            await axiosClient.post(`/api/v1/support/tickets/${ticketId}/comments`, {
                content: newComment,
                is_internal: false
            });
            setNewComment('');
            fetchTicketDetails();
        } catch (error) {
            console.error('Error adding comment:', error);
            alert('Failed to add comment');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="text-center py-8">Loading...</div>;
    if (!ticket) return <div className="text-center py-8 text-red-600">Ticket not found</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Ticket Header */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">{ticket.title}</h1>
                        <p className="text-gray-600">Ticket: <span className="font-mono font-bold">{ticket.ticket_number}</span></p>
                    </div>
                    <div className="text-right">
                        <div className="mb-2">{getPriorityBadge(ticket.priority)}</div>
                        <div>{getStatusBadge(ticket.status)}</div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <p className="text-gray-600">Category</p>
                        <p className="font-medium">{ticket.category.toUpperCase()}</p>
                    </div>
                    <div>
                        <p className="text-gray-600">Created</p>
                        <p className="font-medium">{new Date(ticket.created_at).toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-gray-600">Response Due</p>
                        <p className="font-medium">{new Date(ticket.sla_response_due).toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-gray-600">SLA Status</p>
                        <p className={`font-medium ${ticket.sla_status === 'compliant' ? 'text-green-600' : 'text-red-600'}`}>
                            {ticket.sla_status.toUpperCase()}
                        </p>
                    </div>
                </div>
            </div>

            {/* Description */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4">Description</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
            </div>

            {/* Comments */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4">Comments ({comments.length})</h2>

                {/* Comments List */}
                <div className="space-y-4 mb-6">
                    {comments.map(comment => (
                        <div key={comment.id} className="border-l-4 border-blue-500 pl-4 py-2">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="font-semibold">{comment.author_type === 'agent' ? '👨💼' : '👤'} {comment.author_type}</p>
                                    <p className="text-sm text-gray-600">{new Date(comment.created_at).toLocaleString()}</p>
                                </div>
                                {comment.is_internal && (
                                    <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">Internal</span>
                                )}
                            </div>
                            <p className="mt-2 text-gray-700">{comment.content}</p>
                        </div>
                    ))}
                </div>

                {/* Add Comment */}
                <form onSubmit={handleAddComment} className="border-t pt-4">
                    <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Add a comment..."
                        rows="4"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                    />
                    <button
                        type="submit"
                        disabled={submitting || !newComment.trim()}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                        {submitting ? 'Posting...' : 'Post Comment'}
                    </button>
                </form>
            </div>
        </div>
    );
}

function getStatusBadge(status) {
    const statusColors = {
        'open': 'bg-red-100 text-red-800',
        'in_progress': 'bg-blue-100 text-blue-800',
        'waiting_customer': 'bg-yellow-100 text-yellow-800',
        'resolved': 'bg-green-100 text-green-800',
        'closed': 'bg-gray-100 text-gray-800',
    };

    return <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[status] || 'bg-gray-100'}`}>
        {status.replace('_', ' ').toUpperCase()}
    </span>;
}

function getPriorityBadge(priority) {
    const priorityColors = {
        'critical': 'bg-red-500 text-white',
        'high': 'bg-orange-500 text-white',
        'medium': 'bg-yellow-500 text-white',
        'low': 'bg-green-500 text-white',
    };

    return <span className={`px-2 py-1 rounded text-xs font-bold ${priorityColors[priority] || 'bg-gray-500'}`}>
        {priority.toUpperCase()}
    </span>;
}
