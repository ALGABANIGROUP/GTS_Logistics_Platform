// src/components/bots/panels/customer-service/TicketSystem.jsx
import React, { useState, useEffect, useRef } from 'react';
import { customerServiceAPI } from '../../../../services/customerService';
import { metaDataService } from '../../../../services/metaDataService';
import './TicketSystem.css';

const TicketSystem = ({ onNewNotification, webSocket }) => {
    const [tickets, setTickets] = useState([]);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [filters, setFilters] = useState({
        status: 'all',
        priority: 'all',
        assignedTo: 'all',
        search: ''
    });
    const [loading, setLoading] = useState(false);
    const [agents, setAgents] = useState([]);
    const [newComment, setNewComment] = useState('');
    const commentInputRef = useRef(null);

    // New Ticket Form State
    const [newTicket, setNewTicket] = useState({
        subject: '',
        description: '',
        priority: 'medium',
        category: 'general',
        location: '',
        customerId: '',
        customerName: '',
        customerEmail: ''
    });

    // Dynamic meta data
    const [trailerTypes, setTrailerTypes] = useState([]);
    const [locations, setLocations] = useState([]);

    useEffect(() => {
        metaDataService.getTrailerTypes().then(setTrailerTypes);
        metaDataService.getLocations().then(setLocations);
    }, []);

    useEffect(() => {
        loadTickets();
        loadAgents();
    }, [filters]);

    useEffect(() => {
        if (webSocket) {
            webSocket.addEventListener('message', handleWebSocketMessage);
            return () => webSocket.removeEventListener('message', handleWebSocketMessage);
        }
    }, [webSocket]);

    const handleWebSocketMessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case 'new_ticket':
                loadTickets();
                onNewNotification('New ticket created', '');
                break;
            case 'ticket_updated':
                loadTickets();
                if (selectedTicket?.id === data.ticketId) {
                    loadTicketDetails(data.ticketId);
                }
                break;
            case 'ticket_assigned':
                loadTickets();
                onNewNotification(`Ticket assigned to ${data.agentName}`, '');
                break;
            case 'ticket_closed':
                loadTickets();
                onNewNotification('Ticket closed', '');
                break;
            default:
                break;
        }
    };

    const loadTickets = async () => {
        setLoading(true);
        try {
            const filterParams = {};

            if (filters.status !== 'all') filterParams.status = filters.status;
            if (filters.priority !== 'all') filterParams.priority = filters.priority;
            if (filters.assignedTo !== 'all') filterParams.assigned_to = filters.assignedTo;
            if (filters.search) filterParams.search = filters.search;

            const ticketList = await customerServiceAPI.getTickets(filterParams);
            setTickets(ticketList);
        } catch (error) {
            console.error('Failed to load tickets:', error);
            onNewNotification('Failed to load tickets', '');
        } finally {
            setLoading(false);
        }
    };

    const loadAgents = async () => {
        try {
            const agentList = await customerServiceAPI.getTopAgents();
            setAgents(agentList);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const loadTicketDetails = async (ticketId) => {
        try {
            const ticket = await customerServiceAPI.getTickets({ id: ticketId });
            if (ticket && ticket.length > 0) {
                setSelectedTicket(ticket[0]);
            }
        } catch (error) {
            console.error('Failed to load ticket details:', error);
        }
    };

    const createTicket = async (e) => {
        e.preventDefault();

        try {
            const ticketData = {
                ...newTicket,
                created_at: new Date().toISOString(),
                status: 'open',
                created_by: 'current_user' // Replace with actual user
            };

            await customerServiceAPI.createTicket(ticketData);

            onNewNotification('Ticket created successfully', '');
            setShowCreateForm(false);
            setNewTicket({
                subject: '',
                description: '',
                priority: 'medium',
                category: 'general',
                customerId: '',
                customerName: '',
                customerEmail: ''
            });

            loadTickets();
        } catch (error) {
            console.error('Failed to create ticket:', error);
            onNewNotification('Failed to create ticket', '');
        }
    };

    const updateTicketStatus = async (ticketId, newStatus) => {
        try {
            await customerServiceAPI.updateTicket(ticketId, { status: newStatus });
            onNewNotification('Ticket status updated', '');
            loadTickets();
            if (selectedTicket?.id === ticketId) {
                loadTicketDetails(ticketId);
            }
        } catch (error) {
            console.error('Failed to update ticket status:', error);
            onNewNotification('Failed to update status', '');
        }
    };

    const updateTicketPriority = async (ticketId, newPriority) => {
        try {
            await customerServiceAPI.updateTicket(ticketId, { priority: newPriority });
            onNewNotification('Ticket priority updated', '');
            loadTickets();
            if (selectedTicket?.id === ticketId) {
                loadTicketDetails(ticketId);
            }
        } catch (error) {
            console.error('Failed to update priority:', error);
            onNewNotification('Failed to update priority', '');
        }
    };

    const assignTicket = async (ticketId, agentId) => {
        try {
            await customerServiceAPI.updateTicket(ticketId, { assigned_to: agentId });
            onNewNotification('Ticket assigned successfully', '');
            loadTickets();
            if (selectedTicket?.id === ticketId) {
                loadTicketDetails(ticketId);
            }
        } catch (error) {
            console.error('Failed to assign ticket:', error);
            onNewNotification('Failed to assign ticket', '');
        }
    };

    const closeTicket = async (ticketId) => {
        try {
            await customerServiceAPI.closeTicket(ticketId);
            onNewNotification('Ticket closed successfully', '');
            loadTickets();
            if (selectedTicket?.id === ticketId) {
                setSelectedTicket(null);
            }
        } catch (error) {
            console.error('Failed to close ticket:', error);
            onNewNotification('Failed to close ticket', '');
        }
    };

    const addComment = async () => {
        if (!newComment.trim() || !selectedTicket) return;

        try {
            const comment = {
                text: newComment,
                created_by: 'current_user', // Replace with actual user
                created_at: new Date().toISOString()
            };

            const updatedComments = [...(selectedTicket.comments || []), comment];
            await customerServiceAPI.updateTicket(selectedTicket.id, { comments: updatedComments });

            onNewNotification('Comment added', '');
            setNewComment('');
            loadTicketDetails(selectedTicket.id);
        } catch (error) {
            console.error('Failed to add comment:', error);
            onNewNotification('Failed to add comment', '');
        }
    };

    const getPriorityColor = (priority) => {
        const colors = {
            urgent: '#ef4444',
            high: '#f97316',
            medium: '#eab308',
            low: '#22c55e'
        };
        return colors[priority] || colors.medium;
    };

    const getStatusColor = (status) => {
        const colors = {
            open: '#3b82f6',
            'in-progress': '#eab308',
            resolved: '#22c55e',
            closed: '#64748b'
        };
        return colors[status] || colors.open;
    };

    const filteredTickets = tickets.filter(ticket => {
        if (filters.search) {
            const search = filters.search.toLowerCase();
            return (
                ticket.subject?.toLowerCase().includes(search) ||
                ticket.description?.toLowerCase().includes(search) ||
                ticket.id?.toString().includes(search)
            );
        }
        return true;
    });

    return (
        <div className="ticket-system">
            {/* Header with Actions */}
            <div className="ticket-header">
                <div className="header-left">
                    <h2> Support Tickets</h2>
                    <span className="ticket-count">{filteredTickets.length} tickets</span>
                </div>
                <div className="header-actions">
                    <button
                        className="btn-create-ticket"
                        onClick={() => setShowCreateForm(true)}
                    >
                         Create Ticket
                    </button>
                    <button
                        className="btn-refresh"
                        onClick={loadTickets}
                        disabled={loading}
                    >
                         Refresh
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="ticket-filters">
                <div className="filter-group">
                    <label> Search</label>
                    <input
                        type="text"
                        placeholder="Search by subject, ID, or description..."
                        value={filters.search}
                        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                        className="filter-search"
                    />
                </div>

                <div className="filter-group">
                    <label>Status</label>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                        className="filter-select"
                    >
                        <option value="all">All Statuses</option>
                        <option value="open">Open</option>
                        <option value="in-progress">In Progress</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label>Priority</label>
                    <select
                        value={filters.priority}
                        onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                        className="filter-select"
                    >
                        <option value="all">All Priorities</option>
                        <option value="urgent"> Urgent</option>
                        <option value="high"> High</option>
                        <option value="medium"> Medium</option>
                        <option value="low"> Low</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label>Assigned To</label>
                    <select
                        value={filters.assignedTo}
                        onChange={(e) => setFilters({ ...filters, assignedTo: e.target.value })}
                        className="filter-select"
                    >
                        <option value="all">All Agents</option>
                        <option value="unassigned">Unassigned</option>
                        {agents.map(agent => (
                            <option key={agent.id} value={agent.id}>
                                {agent.name}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="ticket-content">
                {/* Ticket List */}
                <div className="ticket-list">
                    {loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Loading tickets...</p>
                        </div>
                    ) : filteredTickets.length === 0 ? (
                        <div className="empty-state">
                            <span className="empty-icon"></span>
                            <h3>No Tickets Found</h3>
                            <p>No tickets match your current filters</p>
                        </div>
                    ) : (
                        filteredTickets.map(ticket => (
                            <div
                                key={ticket.id}
                                className={`ticket-card ${selectedTicket?.id === ticket.id ? 'selected' : ''}`}
                                onClick={() => setSelectedTicket(ticket)}
                            >
                                <div className="ticket-card-header">
                                    <div className="ticket-id">#{ticket.id}</div>
                                    <div
                                        className="ticket-priority"
                                        style={{ background: getPriorityColor(ticket.priority) }}
                                    >
                                        {ticket.priority}
                                    </div>
                                </div>

                                <h4 className="ticket-subject">{ticket.subject}</h4>

                                <p className="ticket-description">
                                    {ticket.description?.substring(0, 100)}
                                    {ticket.description?.length > 100 ? '...' : ''}
                                </p>

                                <div className="ticket-card-footer">
                                    <div
                                        className="ticket-status"
                                        style={{ background: getStatusColor(ticket.status) }}
                                    >
                                        {ticket.status}
                                    </div>
                                    <span className="ticket-time">
                                        {new Date(ticket.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Ticket Details Sidebar */}
                {selectedTicket && (
                    <div className="ticket-details">
                        <div className="details-header">
                            <h3>Ticket #{selectedTicket.id}</h3>
                            <button
                                className="btn-close-sidebar"
                                onClick={() => setSelectedTicket(null)}
                            >
                                
                            </button>
                        </div>

                        <div className="details-content">
                            {/* Subject */}
                            <div className="detail-section">
                                <h4>{selectedTicket.subject}</h4>
                                <p className="ticket-full-description">
                                    {selectedTicket.description}
                                </p>
                            </div>

                            {/* Status & Priority Controls */}
                            <div className="detail-section">
                                <div className="control-group">
                                    <label>Status</label>
                                    <select
                                        value={selectedTicket.status}
                                        onChange={(e) => updateTicketStatus(selectedTicket.id, e.target.value)}
                                        className="control-select"
                                        style={{ borderColor: getStatusColor(selectedTicket.status) }}
                                    >
                                        <option value="open">Open</option>
                                        <option value="in-progress">In Progress</option>
                                        <option value="resolved">Resolved</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                </div>

                                <div className="control-group">
                                    <label>Priority</label>
                                    <select
                                        value={selectedTicket.priority}
                                        onChange={(e) => updateTicketPriority(selectedTicket.id, e.target.value)}
                                        className="control-select"
                                        style={{ borderColor: getPriorityColor(selectedTicket.priority) }}
                                    >
                                        <option value="low"> Low</option>
                                        <option value="medium"> Medium</option>
                                        <option value="high"> High</option>
                                        <option value="urgent"> Urgent</option>
                                    </select>
                                </div>

                                <div className="control-group">
                                    <label>Assign To</label>
                                    <select
                                        value={selectedTicket.assigned_to || ''}
                                        onChange={(e) => assignTicket(selectedTicket.id, e.target.value)}
                                        className="control-select"
                                    >
                                        <option value="">Unassigned</option>
                                        {agents.map(agent => (
                                            <option key={agent.id} value={agent.id}>
                                                {agent.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Customer Info */}
                            <div className="detail-section">
                                <h4>Customer Information</h4>
                                <div className="info-grid">
                                    <div className="info-item">
                                        <span className="info-label">Name:</span>
                                        <span className="info-value">{selectedTicket.customerName || 'N/A'}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Email:</span>
                                        <span className="info-value">{selectedTicket.customerEmail || 'N/A'}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">ID:</span>
                                        <span className="info-value">{selectedTicket.customerId || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Comments Section */}
                            <div className="detail-section">
                                <h4>Comments & Notes</h4>
                                <div className="comments-list">
                                    {selectedTicket.comments && selectedTicket.comments.length > 0 ? (
                                        selectedTicket.comments.map((comment, index) => (
                                            <div key={index} className="comment-item">
                                                <div className="comment-header">
                                                    <span className="comment-author">{comment.created_by}</span>
                                                    <span className="comment-time">
                                                        {new Date(comment.created_at).toLocaleString()}
                                                    </span>
                                                </div>
                                                <p className="comment-text">{comment.text}</p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="no-comments">No comments yet</p>
                                    )}
                                </div>

                                <div className="comment-input-container">
                                    <textarea
                                        ref={commentInputRef}
                                        value={newComment}
                                        onChange={(e) => setNewComment(e.target.value)}
                                        placeholder="Add a comment or note..."
                                        className="comment-input"
                                        rows="3"
                                    />
                                    <button
                                        onClick={addComment}
                                        disabled={!newComment.trim()}
                                        className="btn-add-comment"
                                    >
                                         Add Comment
                                    </button>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="detail-actions">
                                <button
                                    onClick={() => closeTicket(selectedTicket.id)}
                                    className="btn-close-ticket"
                                    disabled={selectedTicket.status === 'closed'}
                                >
                                     Close Ticket
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Create Ticket Modal */}
            {showCreateForm && (
                <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3> Create New Ticket</h3>
                            <button
                                className="btn-close-modal"
                                onClick={() => setShowCreateForm(false)}
                            >
                                
                            </button>
                        </div>

                        <form onSubmit={createTicket} className="create-ticket-form">
                            <div className="form-group">
                                <label>Subject *</label>
                                <input
                                    type="text"
                                    value={newTicket.subject}
                                    onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                                    placeholder="Brief description of the issue"
                                    required
                                    className="form-input"
                                />
                            </div>

                            <div className="form-group">
                                <label>Description *</label>
                                <textarea
                                    value={newTicket.description}
                                    onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                                    placeholder="Detailed description of the issue"
                                    required
                                    rows="5"
                                    className="form-textarea"
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Priority</label>
                                    <select
                                        value={newTicket.priority}
                                        onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="low"> Low</option>
                                        <option value="medium"> Medium</option>
                                        <option value="high"> High</option>
                                        <option value="urgent"> Urgent</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Category</label>
                                    <select
                                        value={newTicket.category}
                                        onChange={(e) => setNewTicket({ ...newTicket, category: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="general">General</option>
                                        <option value="technical">Technical</option>
                                        <option value="billing">Billing</option>
                                        <option value="feature_request">Feature Request</option>
                                        <option value="bug_report">Bug Report</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Trailer Type</label>
                                    <select
                                        value={newTicket.trailerType || ''}
                                        onChange={(e) => setNewTicket({ ...newTicket, trailerType: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="">Select Trailer Type</option>
                                        {trailerTypes.map((type, idx) => (
                                            <option key={idx} value={type}>{type}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Location</label>
                                    <select
                                        value={newTicket.location || ''}
                                        onChange={(e) => setNewTicket({ ...newTicket, location: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="">Select Location</option>
                                        {locations.map((loc, idx) => (
                                            <option key={idx} value={loc}>{loc}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Customer Name</label>
                                <input
                                    type="text"
                                    value={newTicket.customerName}
                                    onChange={(e) => setNewTicket({ ...newTicket, customerName: e.target.value })}
                                    placeholder="Customer name"
                                    className="form-input"
                                />
                            </div>

                            <div className="form-group">
                                <label>Customer Email</label>
                                <input
                                    type="email"
                                    value={newTicket.customerEmail}
                                    onChange={(e) => setNewTicket({ ...newTicket, customerEmail: e.target.value })}
                                    placeholder="customer@example.com"
                                    className="form-input"
                                />
                            </div>

                            <div className="form-actions">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateForm(false)}
                                    className="btn-cancel"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn-submit"
                                >
                                     Create Ticket
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TicketSystem;
